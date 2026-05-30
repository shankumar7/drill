from abc import ABC, abstractmethod

from backend.core.types import PoseDetection, RuleResult


class EvaluationRule(ABC):
    name: str

    @abstractmethod
    def evaluate(self, detection: PoseDetection) -> RuleResult:
        raise NotImplementedError
