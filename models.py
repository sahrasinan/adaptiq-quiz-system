"""
models.py — AdaptIQ Uyarlanabilir Sınav Sistemi için temel OOP veri modelleri.
"""

from __future__ import annotations
import time
import random
from dataclasses import dataclass, field
from typing import Optional


# ---------------------------------------------------------------------------
# Soru (Question)
# ---------------------------------------------------------------------------

@dataclass
class Question:
    """Tek bir sınav sorusunu temsil eder."""
    id: str
    topic: str
    difficulty: int          # 1 (kolay) → 3 (zor)
    text: str
    options: list[str]       # tam olarak 4 seçenek
    answer_index: int        # 0 tabanlı seçenek indeksi
    explanation: str = ""

    def is_correct(self, chosen_index: int) -> bool:
        return chosen_index == self.answer_index

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "topic": self.topic,
            "difficulty": self.difficulty,
            "text": self.text,
            "options": self.options,
            "answer_index": self.answer_index,
            "explanation": self.explanation,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Question":
        return cls(
            id=data["id"],
            topic=data["topic"],
            difficulty=int(data["difficulty"]),
            text=data["text"],
            options=data["options"],
            answer_index=int(data["answer_index"]),
            explanation=data.get("explanation", ""),
        )


# ---------------------------------------------------------------------------
# Uyarlanabilir Motor (AdaptiveEngine)
# ---------------------------------------------------------------------------

class AdaptiveEngine:
    """
    Şimdiye kadarki performansa göre bir sonraki soruyu belirler.

    Strateji
    --------
    * Her konu için bir ağırlık tutulur (varsayılan 1.0).
    * Yanlış cevap → o konunun ağırlığı YANLIS_ARTIS kadar artar.
    * Doğru cevap  → ağırlık DOGRU_AZALIS kadar düşer (taban 1.0).
    * Her adımda konu ağırlıklarıyla orantılı olarak rastgele seçim yapılır;
      aynı oturumda aynı soru tekrar sorulmaz.
    """

    YANLIS_ARTIS  = 2.0
    DOGRU_AZALIS  = 0.5

    def __init__(self, questions: list[Question]) -> None:
        self.all_questions: list[Question] = questions
        self.topic_weights: dict[str, float] = {}
        self.asked_ids: set[str] = set()

        for q in questions:
            self.topic_weights.setdefault(q.topic, 1.0)

    def record_answer(self, question: Question, correct: bool) -> None:
        topic = question.topic
        if correct:
            self.topic_weights[topic] = max(
                1.0, self.topic_weights[topic] - self.DOGRU_AZALIS
            )
        else:
            self.topic_weights[topic] += self.YANLIS_ARTIS

    def next_question(self) -> Optional[Question]:
        """Sonraki soruyu döndürür; havuz tükendiyse None."""
        remaining = [q for q in self.all_questions if q.id not in self.asked_ids]
        if not remaining:
            return None
        weights = [self.topic_weights.get(q.topic, 1.0) for q in remaining]
        chosen  = random.choices(remaining, weights=weights, k=1)[0]
        self.asked_ids.add(chosen.id)
        return chosen

    def reset(self) -> None:
        self.asked_ids.clear()
        self.topic_weights = {t: 1.0 for t in self.topic_weights}


# ---------------------------------------------------------------------------
# Sınav Oturumu (QuizSession)
# ---------------------------------------------------------------------------

@dataclass
class QuizSession:
    """Tek bir sınav denemesinin durumunu izler."""
    questions_total: int
    started_at: float = field(default_factory=time.time)
    finished_at: Optional[float] = None

    # Soru başına kayıtlar: question_id, topic, correct, chosen_index, time_taken
    records: list[dict] = field(default_factory=list)

    @property
    def elapsed(self) -> float:
        end = self.finished_at or time.time()
        return round(end - self.started_at, 2)

    @property
    def answered(self) -> int:
        return len(self.records)

    @property
    def correct_count(self) -> int:
        return sum(1 for r in self.records if r["correct"])

    @property
    def incorrect_count(self) -> int:
        return self.answered - self.correct_count

    @property
    def score_pct(self) -> float:
        if not self.answered:
            return 0.0
        return round(self.correct_count / self.answered * 100, 1)

    def record_answer(self, question: Question, chosen_index: int, time_taken: float) -> bool:
        correct = question.is_correct(chosen_index)
        self.records.append({
            "question_id":  question.id,
            "topic":        question.topic,
            "difficulty":   question.difficulty,
            "correct":      correct,
            "chosen_index": chosen_index,
            "answer_index": question.answer_index,
            "time_taken":   round(time_taken, 2),
        })
        return correct

    def finish(self) -> None:
        self.finished_at = time.time()

    def weak_topics(self) -> dict[str, dict]:
        """Öğrencinin zorlandığı konular için konu başına doğruluk istatistikleri."""
        stats: dict[str, dict] = {}
        for r in self.records:
            t = r["topic"]
            if t not in stats:
                stats[t] = {"correct": 0, "total": 0}
            stats[t]["total"] += 1
            if r["correct"]:
                stats[t]["correct"] += 1

        result = {}
        for topic, s in stats.items():
            acc = round(s["correct"] / s["total"] * 100, 1) if s["total"] else 0
            result[topic] = {"accuracy": acc, **s}
        return dict(sorted(result.items(), key=lambda x: x[1]["accuracy"]))

    def to_dict(self) -> dict:
        return {
            "started_at":      self.started_at,
            "finished_at":     self.finished_at,
            "elapsed":         self.elapsed,
            "questions_total": self.questions_total,
            "answered":        self.answered,
            "correct":         self.correct_count,
            "incorrect":       self.incorrect_count,
            "score_pct":       self.score_pct,
            "records":         self.records,
            "weak_topics":     self.weak_topics(),
        }


# ---------------------------------------------------------------------------
# Öğrenci Profili (StudentProfile)
# ---------------------------------------------------------------------------

@dataclass
class StudentProfile:
    """Birden fazla oturum boyunca kalıcı öğrenci verisi."""
    username: str
    display_name: str
    created_at: float = field(default_factory=time.time)
    history: list[dict] = field(default_factory=list)
    # konu → birikimli doğruluk yüzdesi
    cumulative_weak_topics: dict[str, float] = field(default_factory=dict)

    def add_session(self, session: QuizSession) -> None:
        record = session.to_dict()
        self.history.append(record)
        self._update_weak_topics(record["weak_topics"])

    def _update_weak_topics(self, session_weak: dict[str, dict]) -> None:
        for topic, stats in session_weak.items():
            acc  = stats["accuracy"]
            prev = self.cumulative_weak_topics.get(topic, acc)
            # Ağırlıklı hareketli ortalama: son oturum %40 ağırlık taşır
            self.cumulative_weak_topics[topic] = round(prev * 0.6 + acc * 0.4, 1)

    @property
    def sessions_count(self) -> int:
        return len(self.history)

    @property
    def best_score(self) -> float:
        if not self.history:
            return 0.0
        return max(s["score_pct"] for s in self.history)

    @property
    def avg_score(self) -> float:
        if not self.history:
            return 0.0
        return round(sum(s["score_pct"] for s in self.history) / len(self.history), 1)

    def to_dict(self) -> dict:
        return {
            "username":               self.username,
            "display_name":           self.display_name,
            "created_at":             self.created_at,
            "history":                self.history,
            "cumulative_weak_topics": self.cumulative_weak_topics,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "StudentProfile":
        p = cls(
            username=data["username"],
            display_name=data["display_name"],
            created_at=data.get("created_at", time.time()),
        )
        p.history = data.get("history", [])
        p.cumulative_weak_topics = data.get("cumulative_weak_topics", {})
        return p
