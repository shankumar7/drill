from abc import ABC, abstractmethod

from backend.core.types import PoseDetection, RuleResult


class EvaluationRule(ABC):
    name: str

    @abstractmethod
    def evaluate(self, detection: PoseDetection) -> RuleResult:
        raise NotImplementedError

    def smooth_score(
        self,
        detection: PoseDetection,
        score: float,
        window_size: int = 10,
        min_history: int = 5,
        confidence: float = 1.0,
    ) -> RuleResult | float:
        """Apply a rolling average to smooth the score, weighted by confidence.
        Returns a ``not_evaluable`` RuleResult if insufficient history, otherwise the smoothed float score.
        """
        # Ensure we have a history list for this rule
        history = (
            detection.posture_history.setdefault(self.name, [])
            if detection.posture_history is not None
            else []
        )
        weighted_score = score * confidence
        history.append(weighted_score)
        del history[:-window_size]
        if len(history) < min_history:
            return RuleResult(self.name, "not_evaluable", None, "Collecting stable evidence.")
        return sum(history) / len(history)

    def is_keypoint_visible(self, keypoint: tuple[float, float, float], threshold: float = 0.2) -> bool:
        """Return ``True`` if the keypoint confidence meets ``threshold``.
        ``keypoint`` is expected to be ``(x, y, confidence)``.
        """
        return keypoint[2] >= threshold

    
