import os
import sys

import pytest
from azure.core.exceptions import ResourceModifiedError, ResourceNotFoundError

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from counter import increment  # noqa: E402


class Entity(dict):
    def __init__(self, data, etag):
        super().__init__(data)
        self.metadata = {"etag": etag}


class FakeTable:
    """In-memory stand-in for an Azure Table, with ETag checks."""

    def __init__(self, conflicts=0):
        self.row = None
        self.version = 0
        self.conflicts = conflicts  # number of updates to reject, simulating another visitor

    def get_entity(self, pk, rk):
        if self.row is None:
            raise ResourceNotFoundError("missing")
        return Entity(self.row, str(self.version))

    def create_entity(self, entity):
        self.row = dict(entity)
        self.version += 1

    def update_entity(self, entity, mode, etag, match_condition):
        if self.conflicts:
            self.conflicts -= 1
            self.row["count"] += 1  # another visitor got in first
            self.version += 1
            raise ResourceModifiedError("etag mismatch")
        if etag != str(self.version):
            raise ResourceModifiedError("etag mismatch")
        self.row = dict(entity)
        self.version += 1


def test_first_visit_creates_counter():
    assert increment(FakeTable()) == 1


def test_counts_up():
    table = FakeTable()
    assert [increment(table) for _ in range(3)] == [1, 2, 3]


def test_concurrent_update_is_retried_not_lost():
    table = FakeTable()
    increment(table)                 # count = 1
    table.conflicts = 1              # another visitor updates while we work
    assert increment(table) == 3     # their visit (2) and ours (3) both count


def test_gives_up_after_too_many_conflicts():
    table = FakeTable()
    increment(table)
    table.conflicts = 99
    with pytest.raises(RuntimeError):
        increment(table)
