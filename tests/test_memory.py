"""
MedBotX - Memory Manager Unit Tests
Developed by Bhaskar Shivaji Kumbhar
"""
import pytest
from app.memory.memory_manager import (
    create_session,
    get_temp_memory,
    add_to_temp_memory,
    clear_temp_memory,
)


def test_create_session():
    sid = create_session()
    assert sid
    assert isinstance(sid, str)
    assert len(sid) == 36  # UUID format


def test_add_and_get_memory():
    sid = create_session()
    add_to_temp_memory(sid, "human", "Hello")
    add_to_temp_memory(sid, "ai", "Hi there!")
    history = get_temp_memory(sid)
    assert len(history) == 2
    assert history[0]["role"] == "human"
    assert history[0]["content"] == "Hello"
    assert history[1]["role"] == "ai"


def test_clear_memory():
    sid = create_session()
    add_to_temp_memory(sid, "human", "Test")
    clear_temp_memory(sid)
    result = get_temp_memory(sid)
    assert result == []


def test_memory_trimming():
    sid = create_session()
    for i in range(25):
        add_to_temp_memory(sid, "human", f"Message {i}")
    history = get_temp_memory(sid)
    assert len(history) <= 20
