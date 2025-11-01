"""Database repository for all data access operations."""

from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy import create_engine, select, func, and_, or_
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager
from src.database.models import (
    Base,
    User,
    Topic,
    Question,
    UserProgress,
    QuestionAnalytics,
    ExampleFileValidation,
    QuestionSource,
    ValidationStatus
)
from src.utils.logger import get_logger
from src.utils.exceptions import DatabaseError

logger = get_logger(__name__)


class Repository:
    """Database repository for all data access operations."""

    def __init__(self, db_url: str = "sqlite:///learning_bot.db"):
        """
        Initialize repository with database connection.

        Args:
            db_url: Database connection URL
        """
        self.db_url = db_url
        try:
            self.engine = create_engine(db_url, echo=False)
            self.SessionLocal = sessionmaker(bind=self.engine, expire_on_commit=False)
            logger.info(f"Repository initialized with database: {db_url}")
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            raise DatabaseError(f"Database initialization failed: {e}")

    @contextmanager
    def get_session(self) -> Session:
        """
        Get database session context manager.

        Yields:
            SQLAlchemy session

        Raises:
            DatabaseError: If session operations fail
        """
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Database session error: {e}")
            raise DatabaseError(f"Database operation failed: {e}")
        finally:
            session.close()

    def create_tables(self) -> None:
        """Create all database tables."""
        try:
            Base.metadata.create_all(self.engine)
            logger.info("Database tables created successfully")
        except Exception as e:
            logger.error(f"Failed to create tables: {e}")
            raise DatabaseError(f"Table creation failed: {e}")

    # User operations

    def get_user_by_telegram_id(self, telegram_id: int) -> Optional[User]:
        """
        Get user by telegram ID.

        Args:
            telegram_id: Telegram user ID

        Returns:
            User object if found, None otherwise
        """
        with self.get_session() as session:
            return session.query(User).filter(User.telegram_id == telegram_id).first()

    def create_user(self, telegram_id: int, native_language: str) -> User:
        """
        Create new user.

        Args:
            telegram_id: Telegram user ID
            native_language: User's native language

        Returns:
            Created User object
        """
        with self.get_session() as session:
            user = User(
                telegram_id=telegram_id,
                native_language=native_language,
                created_at=datetime.utcnow()
            )
            session.add(user)
            session.flush()
            session.refresh(user)
            logger.info(f"Created user with telegram_id: {telegram_id}")
            return user

    def get_or_create_user(self, telegram_id: int, native_language: str) -> User:
        """
        Get existing user or create new one.

        Args:
            telegram_id: Telegram user ID
            native_language: User's native language

        Returns:
            User object
        """
        user = self.get_user_by_telegram_id(telegram_id)
        if user is None:
            user = self.create_user(telegram_id, native_language)
        return user

    # Topic operations

    def get_all_topics(self, active_only: bool = True) -> List[Topic]:
        """
        Get all topics.

        Args:
            active_only: Return only active topics

        Returns:
            List of Topic objects
        """
        with self.get_session() as session:
            query = session.query(Topic)
            if active_only:
                query = query.filter(Topic.is_active == True)
            return query.all()

    def get_topic(self, topic_id: int) -> Optional[Topic]:
        """
        Get topic by ID.

        Args:
            topic_id: Topic ID

        Returns:
            Topic object if found, None otherwise
        """
        with self.get_session() as session:
            return session.query(Topic).filter(Topic.id == topic_id).first()

    def get_topic_by_name(self, name: str) -> Optional[Topic]:
        """
        Get topic by name.

        Args:
            name: Topic name

        Returns:
            Topic object if found, None otherwise
        """
        with self.get_session() as session:
            return session.query(Topic).filter(Topic.name == name).first()

    def create_topic(self, name: str, type: str, config: dict, is_active: bool = True) -> Topic:
        """
        Create new topic.

        Args:
            name: Topic name
            type: Topic type (language, history, etc.)
            config: Topic configuration dictionary
            is_active: Whether topic is active

        Returns:
            Created Topic object
        """
        with self.get_session() as session:
            topic = Topic(
                name=name,
                type=type,
                config=config,
                is_active=is_active,
                created_at=datetime.utcnow()
            )
            session.add(topic)
            session.flush()
            session.refresh(topic)
            logger.info(f"Created topic: {name}")
            return topic

    def update_topic(self, topic_id: int, config: dict, is_active: bool = True) -> Optional[Topic]:
        """
        Update existing topic.

        Args:
            topic_id: Topic ID to update
            config: New topic configuration dictionary
            is_active: Whether topic is active

        Returns:
            Updated Topic object if found, None otherwise
        """
        with self.get_session() as session:
            topic = session.query(Topic).filter(Topic.id == topic_id).first()
            if topic:
                topic.config = config
                topic.is_active = is_active
                session.flush()
                session.refresh(topic)
                logger.info(f"Updated topic: {topic.name}")
            return topic

    # Question operations

    def create_question(self, question_data: Dict[str, Any]) -> Question:
        """
        Create new question.

        Args:
            question_data: Dictionary containing question fields

        Returns:
            Created Question object
        """
        with self.get_session() as session:
            question = Question(
                topic_id=question_data['topic_id'],
                question_text=question_data['question_text'],
                choice_a=question_data['choice_a'],
                choice_b=question_data['choice_b'],
                choice_c=question_data['choice_c'],
                choice_d=question_data['choice_d'],
                correct_answer=question_data['correct_answer'],
                explanation=question_data['explanation'],
                difficulty=question_data['difficulty'],
                tags=question_data.get('tags', []),
                source=question_data.get('source', QuestionSource.LLM.value),
                source_file=question_data.get('source_file'),
                created_at=datetime.utcnow(),
                quality_score=question_data.get('quality_score', 0.5)
            )
            session.add(question)
            session.flush()

            # Create analytics entry
            analytics = QuestionAnalytics(
                question_id=question.id,
                total_times_shown=0,
                total_correct=0,
                total_incorrect=0,
                success_rate=0.0,
                last_updated_at=datetime.utcnow(),
                needs_review=False
            )
            session.add(analytics)
            session.flush()
            session.refresh(question)

            logger.info(f"Created question ID: {question.id} for topic_id: {question.topic_id}")
            return question

    def get_question(self, question_id: int) -> Optional[Question]:
        """
        Get question by ID.

        Args:
            question_id: Question ID

        Returns:
            Question object if found, None otherwise
        """
        with self.get_session() as session:
            return session.query(Question).filter(Question.id == question_id).first()

    def get_next_question(self, user_id: int, topic_id: int) -> Optional[Question]:
        """
        Get next question based on spaced repetition algorithm.

        Priority:
        1. Questions due for review (next_review_at <= now)
        2. Questions never seen by user
        3. Questions with lowest consecutive_correct count

        Args:
            user_id: User ID
            topic_id: Topic ID

        Returns:
            Question object or None if no questions available
        """
        with self.get_session() as session:
            now = datetime.utcnow()

            # Get all questions for topic
            all_questions = session.query(Question).filter(
                Question.topic_id == topic_id
            ).all()

            if not all_questions:
                return None

            all_question_ids = [q.id for q in all_questions]

            # Get user progress for all questions
            progress_map = {}
            progresses = session.query(UserProgress).filter(
                and_(
                    UserProgress.user_id == user_id,
                    UserProgress.question_id.in_(all_question_ids)
                )
            ).all()

            for prog in progresses:
                progress_map[prog.question_id] = prog

            # Priority 1: Questions due for review
            due_questions = []
            for q in all_questions:
                prog = progress_map.get(q.id)
                if prog and prog.next_review_at and prog.next_review_at <= now:
                    due_questions.append((q, prog))

            if due_questions:
                # Sort by next_review_at (oldest first)
                due_questions.sort(key=lambda x: x[1].next_review_at)
                logger.info(f"Selected due question ID: {due_questions[0][0].id}")
                return due_questions[0][0]

            # Priority 2: Questions never seen
            unseen_questions = []
            for q in all_questions:
                if q.id not in progress_map:
                    unseen_questions.append(q)

            if unseen_questions:
                # Return first unseen question (could randomize here)
                logger.info(f"Selected unseen question ID: {unseen_questions[0].id}")
                return unseen_questions[0]

            # Priority 3: Questions with lowest consecutive_correct
            if all_questions:
                questions_with_progress = [
                    (q, progress_map.get(q.id, None)) for q in all_questions
                ]
                # Sort by consecutive_correct (ascending)
                questions_with_progress.sort(
                    key=lambda x: x[1].consecutive_correct if x[1] else 0
                )
                selected_q = questions_with_progress[0][0]
                logger.info(f"Selected low-mastery question ID: {selected_q.id}")
                return selected_q

            return None

    # Progress operations

    def update_progress(
        self,
        user_id: int,
        question_id: int,
        is_correct: bool,
        response_time: Optional[float] = None
    ) -> None:
        """
        Update user progress for a question using spaced repetition.

        Intervals:
        - Correct: multiply interval by 2 (1h, 2h, 4h, 8h, 16h, etc.)
        - Incorrect: reset to 1 hour

        Args:
            user_id: User ID
            question_id: Question ID
            is_correct: Whether answer was correct
            response_time: Response time in seconds
        """
        with self.get_session() as session:
            # Get or create progress
            progress = session.query(UserProgress).filter(
                and_(
                    UserProgress.user_id == user_id,
                    UserProgress.question_id == question_id
                )
            ).first()

            now = datetime.utcnow()

            if progress is None:
                # Create new progress
                progress = UserProgress(
                    user_id=user_id,
                    question_id=question_id,
                    times_shown=1,
                    times_correct=1 if is_correct else 0,
                    times_incorrect=0 if is_correct else 1,
                    consecutive_correct=1 if is_correct else 0,
                    last_shown_at=now,
                    next_review_at=now + timedelta(hours=1 if is_correct else 1),
                    average_response_time=response_time
                )
                session.add(progress)
            else:
                # Update existing progress
                progress.times_shown += 1
                progress.last_shown_at = now

                if is_correct:
                    progress.times_correct += 1
                    progress.consecutive_correct += 1

                    # Spaced repetition: double interval (min 1h, max ~30 days)
                    interval_hours = min(2 ** progress.consecutive_correct, 720)  # max 30 days
                    progress.next_review_at = now + timedelta(hours=interval_hours)
                else:
                    progress.times_incorrect += 1
                    progress.consecutive_correct = 0

                    # Reset to 1 hour
                    progress.next_review_at = now + timedelta(hours=1)

                # Update average response time
                if response_time is not None:
                    if progress.average_response_time is None:
                        progress.average_response_time = response_time
                    else:
                        # Rolling average
                        progress.average_response_time = (
                            progress.average_response_time * 0.7 + response_time * 0.3
                        )

            logger.info(
                f"Updated progress for user {user_id}, question {question_id}: "
                f"correct={is_correct}, consecutive={progress.consecutive_correct}"
            )

    # Analytics operations

    def get_user_stats(self, user_id: int, topic_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Get user statistics.

        Args:
            user_id: User ID
            topic_id: Optional topic ID to filter by

        Returns:
            Dictionary with statistics
        """
        with self.get_session() as session:
            query = session.query(UserProgress).filter(UserProgress.user_id == user_id)

            if topic_id:
                # Join with Question to filter by topic
                query = query.join(Question).filter(Question.topic_id == topic_id)

            progresses = query.all()

            if not progresses:
                return {
                    'total_questions_seen': 0,
                    'total_correct': 0,
                    'total_incorrect': 0,
                    'accuracy': 0.0,
                    'average_response_time': None,
                    'questions_mastered': 0  # consecutive_correct >= 3
                }

            total_correct = sum(p.times_correct for p in progresses)
            total_incorrect = sum(p.times_incorrect for p in progresses)
            total_attempts = total_correct + total_incorrect

            response_times = [p.average_response_time for p in progresses if p.average_response_time]
            avg_response_time = sum(response_times) / len(response_times) if response_times else None

            questions_mastered = sum(1 for p in progresses if p.consecutive_correct >= 3)

            return {
                'total_questions_seen': len(progresses),
                'total_correct': total_correct,
                'total_incorrect': total_incorrect,
                'accuracy': total_correct / total_attempts if total_attempts > 0 else 0.0,
                'average_response_time': avg_response_time,
                'questions_mastered': questions_mastered
            }

    def update_question_analytics(self, question_id: int) -> None:
        """
        Update question analytics based on user progress.

        Args:
            question_id: Question ID
        """
        with self.get_session() as session:
            # Get analytics
            analytics = session.query(QuestionAnalytics).filter(
                QuestionAnalytics.question_id == question_id
            ).first()

            if not analytics:
                analytics = QuestionAnalytics(
                    question_id=question_id,
                    total_times_shown=0,
                    total_correct=0,
                    total_incorrect=0,
                    success_rate=0.0,
                    last_updated_at=datetime.utcnow(),
                    needs_review=False
                )
                session.add(analytics)

            # Aggregate from user progress
            progresses = session.query(UserProgress).filter(
                UserProgress.question_id == question_id
            ).all()

            if progresses:
                analytics.total_times_shown = sum(p.times_shown for p in progresses)
                analytics.total_correct = sum(p.times_correct for p in progresses)
                analytics.total_incorrect = sum(p.times_incorrect for p in progresses)

                total_attempts = analytics.total_correct + analytics.total_incorrect
                analytics.success_rate = (
                    analytics.total_correct / total_attempts if total_attempts > 0 else 0.0
                )

                # Calculate average response time
                response_times = [p.average_response_time for p in progresses if p.average_response_time]
                analytics.average_response_time = (
                    sum(response_times) / len(response_times) if response_times else None
                )

                # Mark for review if success rate is low
                analytics.needs_review = analytics.success_rate < 0.4 and total_attempts >= 5

                analytics.last_updated_at = datetime.utcnow()

                logger.info(
                    f"Updated analytics for question {question_id}: "
                    f"success_rate={analytics.success_rate:.2f}, needs_review={analytics.needs_review}"
                )

    def get_low_quality_questions(self, threshold: float = 0.4, min_attempts: int = 5) -> List[Question]:
        """
        Get questions with low success rate.

        Args:
            threshold: Success rate threshold (0-1)
            min_attempts: Minimum number of attempts

        Returns:
            List of Question objects
        """
        with self.get_session() as session:
            analytics = session.query(QuestionAnalytics).filter(
                and_(
                    QuestionAnalytics.success_rate < threshold,
                    QuestionAnalytics.total_times_shown >= min_attempts
                )
            ).all()

            question_ids = [a.question_id for a in analytics]
            questions = session.query(Question).filter(Question.id.in_(question_ids)).all()

            return questions

    # Example file validation operations

    def log_validation(
        self,
        file_path: str,
        status: ValidationStatus,
        errors: List[str],
        question_count: int
    ) -> None:
        """
        Log example file validation result.

        Args:
            file_path: Path to example file
            status: Validation status
            errors: List of validation errors
            question_count: Number of questions in file
        """
        with self.get_session() as session:
            validation = session.query(ExampleFileValidation).filter(
                ExampleFileValidation.file_path == file_path
            ).first()

            if validation:
                validation.validation_status = status.value
                validation.validation_errors = errors
                validation.last_validated_at = datetime.utcnow()
                validation.question_count = question_count
            else:
                validation = ExampleFileValidation(
                    file_path=file_path,
                    validation_status=status.value,
                    validation_errors=errors,
                    last_validated_at=datetime.utcnow(),
                    question_count=question_count
                )
                session.add(validation)

            logger.info(f"Logged validation for {file_path}: {status.value}")
