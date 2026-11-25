import random
import sys
import threading
import time
from dataclasses import dataclass, field


@dataclass
class Warehouse:
    name: str
    meds: int
    price_per_unit: float
    use_lock: bool = True
    race_delay: float = 0.0
    lock: threading.Lock = field(default_factory=threading.Lock, repr=False)
    initial_meds: int = field(init=False)
    stolen_meds: int = field(default=0, init=False)

    def __post_init__(self) -> None:
        self.initial_meds = self.meds

    def _execute_steal(self, amount: int) -> tuple[int, bool]:
        """Повертає (фактично_вкрадено, чи_спіймали_бігунка)."""
        # 20% шанс, що бігунка спіймають на спробі
        if random.random() < 0.20:
            return 0, True

        # 15% шанс невдалої спроби (нічого не виніс, але не спіймали)
        if random.random() < 0.15 or self.meds <= 0:
            return 0, False

        # Рандомна фактично винесена кількість (не більше, ніж хотів і ніж є на складі)
        desired = random.randint(1, amount)
        if self.meds <= 0:
            return 0, False

        # Штучна пауза між перевіркою наявності та списанням для демонстрації race condition
        if self.race_delay > 0:
            time.sleep(self.race_delay)

        stolen = min(desired, self.meds)
        self.meds -= stolen
        self.stolen_meds += stolen
        return stolen, False

    def steal(self, amount: int) -> tuple[int, bool]:
        if self.use_lock:
            with self.lock:
                return self._execute_steal(amount)
        return self._execute_steal(amount)


class Runner(threading.Thread):
    def __init__(
        self,
        name: str,
        warehouses: list[Warehouse],
        progress: dict[str, int],
        progress_lock: threading.Lock,
        total_attempts: int = 10,
        fast_mode: bool = False,
    ) -> None:
        super().__init__(name=name)
        self.warehouses = warehouses
        self.progress = progress
        self.progress_lock = progress_lock
        self.total_attempts = total_attempts
        self.fast_mode = fast_mode
        self.profit: float = 0.0
        self.stolen_total: int = 0
        self.caught: bool = False

    def run(self) -> None:
        for attempt in range(1, self.total_attempts + 1):
            warehouse = random.choice(self.warehouses)
            amount = random.randint(10, 30)

            stolen, was_caught = warehouse.steal(amount)
            if was_caught:
                self.caught = True
                with self.progress_lock:
                    self.progress[self.name] = self.total_attempts
                break

            self.stolen_total += stolen
            self.profit += stolen * warehouse.price_per_unit

            with self.progress_lock:
                self.progress[self.name] = attempt

            if not self.fast_mode:
                time.sleep(random.uniform(0.1, 0.5))


def render_progress_bars(
    runners: list[Runner],
    progress: dict[str, int],
    total_attempts: int,
    first_draw: bool,
) -> None:
    lines = []
    for r in runners:
        done = progress.get(r.name, 0)
        bar = "█" * done + "░" * (total_attempts - done)
        status = "СПІЙМАНИЙ" if r.caught else ("ГОТОВО" if done == total_attempts else "В ПРОЦЕСІ")
        lines.append(f"  {r.name:<10} [{bar}] {done:>2}/{total_attempts} ({status})")

    if not first_draw:
        sys.stdout.write(f"\033[{len(lines)}A")
    sys.stdout.write("\n".join(lines) + "\n")
    sys.stdout.flush()


def verify_invariants(warehouses: list[Warehouse], runners: list[Runner]) -> None:
    # 1. На жодному складі не менше нуля медикаментів
    for w in warehouses:
        assert w.meds >= 0, f"Інваріант 1 зламано на {w.name}: meds={w.meds} < 0"

    # 2. Для кожного складу: було = залишилось + вкрали
    for w in warehouses:
        assert w.initial_meds == w.meds + w.stolen_meds, (
            f"Інваріант 2 зламано на {w.name}: "
            f"initial={w.initial_meds} != meds({w.meds}) + stolen({w.stolen_meds})"
        )

    # 3. Загальний прибуток = усе вкрадене * price_per_unit
    expected_profit = round(sum(w.stolen_meds * w.price_per_unit for w in warehouses), 6)
    runners_profit = round(sum(r.profit for r in runners), 6)
    assert expected_profit == runners_profit, (
        f"Інваріант 3 зламано: по складах={expected_profit} != по бігунах={runners_profit}"
    )


def run_simulation(
    num_warehouses: int = 4,
    num_runners: int = 5,
    use_lock: bool = True,
    race_delay: float = 0.0,
    show_progress: bool = True,
    fast_mode: bool = False,
) -> tuple[list[Warehouse], list[Runner]]:
    warehouses = [
        Warehouse(
            name=f"Склад-{i + 1}",
            meds=random.randint(100, 300),
            price_per_unit=round(random.uniform(15.0, 45.0), 2),
            use_lock=use_lock,
            race_delay=race_delay,
        )
        for i in range(num_warehouses)
    ]

    total_attempts = 10
    progress_lock = threading.Lock()
    progress = {f"Бігун-{i + 1}": 0 for i in range(num_runners)}

    runners = [
        Runner(
            name=f"Бігун-{i + 1}",
            warehouses=warehouses,
            progress=progress,
            progress_lock=progress_lock,
            total_attempts=total_attempts,
            fast_mode=fast_mode,
        )
        for i in range(num_runners)
    ]

    for r in runners:
        r.start()

    if show_progress:
        first_draw = True
        while any(r.is_alive() for r in runners):
            with progress_lock:
                render_progress_bars(runners, progress, total_attempts, first_draw)
            first_draw = False
            time.sleep(0.08)
        with progress_lock:
            render_progress_bars(runners, progress, total_attempts, first_draw)

    for r in runners:
        r.join()

    return warehouses, runners


def print_report(warehouses: list[Warehouse], runners: list[Runner]) -> None:
    print("\n=== ЗВІТ ПО СКЛАДАХ ===")
    for w in warehouses:
        print(
            f"{w.name}: було {w.initial_meds} | залишилось {w.meds} | "
            f"вкрали {w.stolen_meds} | ціна {w.price_per_unit} грн/од."
        )

    print("\n=== ЗВІТ ПО БІГУНАХ ===")
    for r in runners:
        state = "спійманий" if r.caught else "успішно завершив"
        print(f"{r.name}: виніс {r.stolen_total} од. | заробив {r.profit:.2f} грн ({state})")

    total_profit = sum(r.profit for r in runners)
    print(f"\nЗАГАЛЬНИЙ ПРИБУТОК: {total_profit:.2f} грн")


if __name__ == "__main__":
    # 1. Наочний одиночний запуск із прогрес-баром
    wh, rn = run_simulation(num_warehouses=4, num_runners=5, use_lock=True, show_progress=True)
    verify_invariants(wh, rn)
    print_report(wh, rn)

    # 2. 100 прогонів із перевіркою інваріантів (з lock)
    for run_idx in range(1, 101):
        wh_i, rn_i = run_simulation(use_lock=True, show_progress=False, fast_mode=True)
        verify_invariants(wh_i, rn_i)
    print("\n100 прогонів з lock: усі інваріанти виконано!")

    # 3. Експеримент без lock із паузою time.sleep(0.001) між перевіркою та списанням
    print("\n=== ЕКСПЕРИМЕНТ БЕЗ LOCK ===")
    broken_found = False
    for run_idx in range(1, 101):
        wh_bad, rn_bad = run_simulation(
            num_warehouses=2,
            num_runners=8,
            use_lock=False,
            race_delay=0.001,
            show_progress=False,
            fast_mode=True,
        )
        try:
            verify_invariants(wh_bad, rn_bad)
        except AssertionError as exc:
            print(f"Зламалось на прогоні #{run_idx}: {exc}")
            broken_found = True
            break

    if not broken_found:
        print("За 100 прогонів гонка потоків не встигла проявитись (збільш кількість бігунів).")
