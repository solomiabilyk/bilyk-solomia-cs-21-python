import pytest
from simulation import run_simulation, verify_invariants


def test_100_runs_with_lock_preserve_invariants() -> None:
    for _ in range(100):
        warehouses, runners = run_simulation(
            num_warehouses=4,
            num_runners=5,
            use_lock=True,
            show_progress=False,
            fast_mode=True,
        )
        verify_invariants(warehouses, runners)


def test_without_lock_breaks_invariant() -> None:
    with pytest.raises(AssertionError):
        for _ in range(100):
            warehouses, runners = run_simulation(
                num_warehouses=2,
                num_runners=8,
                use_lock=False,
                race_delay=0.001,
                show_progress=False,
                fast_mode=True,
            )
            verify_invariants(warehouses, runners)