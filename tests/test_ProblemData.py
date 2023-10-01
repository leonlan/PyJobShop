import numpy as np
import pytest
from numpy.testing import assert_allclose, assert_equal, assert_raises

from fjsp import Job, Machine, Operation, PrecedenceType, ProblemData
from fjsp.constants import MAX_VALUE


def test_job_attributes():
    """
    Tests that the attributes of the Job class are set correctly.
    """
    # Let's first test the default values.
    job = Job()

    assert_equal(job.release_date, 0)
    assert_equal(job.deadline, None)
    assert_equal(job.name, None)

    # Now test with some values.
    job = Job(5, 10, "test")

    assert_equal(job.release_date, 5)
    assert_equal(job.deadline, 10)
    assert_equal(job.name, "test")


def test_machine_attributes():
    """
    Tests that the attributes of the Machine class are set correctly.
    """
    # Let's first test the default values.
    machine = Machine()

    assert_equal(machine.name, None)

    # Now test with some values.
    machine = Machine("TestMachine")

    assert_equal(machine.name, "TestMachine")


def test_operation_attributes():
    """
    Tests that the attributes of the Operation class are set correctly.
    """
    operation = Operation(1, [0, 1], "TestOperation")

    assert_equal(operation.job, 1)
    assert_equal(operation.machines, [0, 1])
    assert_equal(operation.name, "TestOperation")

    # Also test that default values are set correctly.
    operation = Operation(1, [1])

    assert_equal(operation.name, None)


def test_operation_raises_when_invalid_arguments():
    """
    Tests that the Operation class raises an error when invalid arguments are
    passed.
    """
    with assert_raises(ValueError):
        # Empty list of machines.
        Operation(1, [])


# TODO test PrecedenceType


def test_problem_data_attributes():
    """
    Tests that the attributes of the ProblemData class are set correctly.
    """
    jobs = [Job() for _ in range(5)]
    machines = [Machine() for _ in range(5)]
    operations = [Operation(idx, [idx]) for idx in range(5)]
    processing_times = np.ones((5, 5), dtype=int)
    precedences = {
        key: [PrecedenceType.END_BEFORE_START]
        for key in ((0, 1), (2, 3), (4, 5))
    }
    horizon = 10
    access_matrix = np.full((5, 5), True)
    setup_times = np.ones((5, 5, 5), dtype=int)

    data = ProblemData(
        jobs,
        machines,
        operations,
        processing_times,
        precedences,
        horizon,
        access_matrix,
        setup_times,
    )

    assert_equal(data.jobs, jobs)
    assert_equal(data.machines, machines)
    assert_equal(data.operations, operations)
    assert_allclose(data.processing_times, processing_times)
    assert_equal(data.precedences, precedences)
    assert_equal(data.horizon, horizon)
    assert_equal(data.access_matrix, access_matrix)
    assert_allclose(data.setup_times, setup_times)

    assert_equal(data.job2ops, [[0], [1], [2], [3], [4]])
    assert_equal(data.machine2ops, [[0], [1], [2], [3], [4]])
    assert_equal(data.num_jobs, 5)
    assert_equal(data.num_machines, 5)
    assert_equal(data.num_operations, 5)


def test_problem_data_default_values():
    """
    Tests that the default values of the ProblemData class are set correctly.
    """
    jobs = [Job() for _ in range(1)]
    machines = [Machine() for _ in range(1)]
    operations = [Operation(idx, [idx]) for idx in range(1)]
    precedences = {(0, 1): [PrecedenceType.END_BEFORE_START]}
    processing_times = np.ones((1, 1), dtype=int)
    data = ProblemData(
        jobs, machines, operations, processing_times, precedences
    )

    assert_equal(data.horizon, MAX_VALUE)
    assert_allclose(data.access_matrix, np.full((1, 1), True))
    assert_allclose(data.setup_times, np.zeros((1, 1, 1), dtype=int))


@pytest.mark.parametrize(
    "processing_times, horizon, access_matrix, setup_times",
    [
        # Negative processing times.
        (np.ones((1, 1)) * -1, 1, np.full((1, 1), True), np.ones((1, 1, 1))),
        # Invalid processing times shape.
        (np.ones((2, 2)), 1, np.full((1, 1), True), np.ones((1, 1, 1))),
        # Negative horizon.
        (np.ones((1, 1)), -1, np.full((1, 1), True), np.ones((1, 1, 1))),
        # Invalid access matrix shape.
        (np.ones((1, 1)), 1, np.full((2, 2), True), np.ones((1, 1, 1))),
        # Negative setup times.
        (np.ones((1, 1)), 1, np.full((1, 1), True), np.ones((1, 1, 1)) * -1),
        # Invalid setup times shape.
        (np.ones((1, 1)), 1, np.full((1, 1), True), np.ones((2, 2, 2))),
    ],
)
def test_problem_data_raises_when_invalid_arguments(
    processing_times: np.ndarray,
    horizon: int,
    access_matrix: np.ndarray,
    setup_times: np.ndarray,
):
    """
    Tests that the ProblemData class raises an error when invalid arguments are
    passed.
    """
    with assert_raises(ValueError):  # negative processing times
        ProblemData(
            [Job()],
            [Machine()],
            [Operation(0, [0])],
            processing_times.astype(int),
            {},
            horizon,
            access_matrix.astype(int),
            setup_times.astype(int),
        )
