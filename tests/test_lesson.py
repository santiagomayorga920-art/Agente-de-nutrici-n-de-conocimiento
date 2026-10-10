import pytest

from nutricion.domain.lesson import InvalidTransition, LessonState, transition


def test_happy_path():
    state = LessonState.PENDING
    for target in (LessonState.AWAITING_ANSWER, LessonState.EVALUATING, LessonState.COMPLETED):
        state = transition(state, target)
    assert state is LessonState.COMPLETED


def test_cannot_skip_waiting_for_answer():
    with pytest.raises(InvalidTransition):
        transition(LessonState.PENDING, LessonState.COMPLETED)


def test_failed_evaluation_returns_to_waiting():
    state = transition(LessonState.EVALUATING, LessonState.AWAITING_ANSWER)
    assert state is LessonState.AWAITING_ANSWER
