"""Callback handlers for inline button interactions."""

import random
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from src.utils.logger import get_logger
from src.bot import get_bot_instance

logger = get_logger(__name__)


def _shuffle_choices(question):
    """
    Shuffle answer choices and return mapping.

    Args:
        question: Question object with choice_a, choice_b, choice_c, choice_d, correct_answer

    Returns:
        tuple: (shuffled_choices dict, answer_mapping dict, correct_displayed str)
            - shuffled_choices: {'A': text, 'B': text, 'C': text, 'D': text}
            - answer_mapping: {'A': original_letter, ...} maps displayed -> original
            - correct_displayed: which letter (A/B/C/D) shows correct answer now
    """
    # Original choices with their labels
    original_choices = [
        ('A', question.choice_a),
        ('B', question.choice_b),
        ('C', question.choice_c),
        ('D', question.choice_d)
    ]

    # Shuffle the list
    shuffled = original_choices.copy()
    random.shuffle(shuffled)

    # Create mappings
    display_labels = ['A', 'B', 'C', 'D']
    shuffled_choices = {}
    answer_mapping = {}
    correct_displayed = None

    for display_label, (original_label, choice_text) in zip(display_labels, shuffled):
        shuffled_choices[display_label] = choice_text
        answer_mapping[display_label] = original_label

        if original_label == question.correct_answer:
            correct_displayed = display_label

    return shuffled_choices, answer_mapping, correct_displayed


async def topic_selection_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle topic selection button click - start quiz for selected topic."""
    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id
    topic_id = int(query.data.split(":")[1])

    logger.info(f"Topic {topic_id} selected by user {user_id}")

    bot_instance = get_bot_instance()
    repository = bot_instance.repository
    topic = repository.get_topic(topic_id)
    if not topic:
        await query.edit_message_text("Topic not found.")
        return

    session = bot_instance.create_session(user_id, topic_id, topic.name)
    await query.edit_message_text(
        f"Starting quiz for: *{topic.name}*\n\nLoading first question...",
        parse_mode="Markdown"
    )

    await _show_next_question(query, user_id, bot_instance)


async def answer_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle answer button click - check answer and update progress."""
    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id
    selected_answer = query.data.split(":")[1]  # This is the displayed letter (shuffled)

    logger.info(f"Answer {selected_answer} selected by user {user_id}")

    bot_instance = get_bot_instance()
    session = bot_instance.get_session(user_id)
    if not session or not session.get('current_question'):
        await query.edit_message_text("No active question. Use /topics to start!")
        return

    question = session['current_question']

    # Map displayed answer back to original position
    answer_mapping = session.get('answer_mapping', {})
    if answer_mapping:
        original_answer = answer_mapping.get(selected_answer, selected_answer)
        logger.debug(f"Mapped displayed answer {selected_answer} -> original {original_answer}")
    else:
        # Fallback if no mapping (shouldn't happen with shuffling)
        original_answer = selected_answer
        logger.warning("No answer mapping found in session, using selected answer directly")

    is_correct = (original_answer == question.correct_answer)

    response_time = None
    if session.get('start_time'):
        response_time = (datetime.utcnow() - session['start_time']).total_seconds()

    repository = bot_instance.repository
    db_user = repository.get_user_by_telegram_id(user_id)
    repository.update_progress(db_user.id, question.id, is_correct, response_time)

    session['questions_answered'] += 1
    if is_correct:
        session['correct_answers'] += 1

    logger.info(
        f"Answer processed: questions_answered={session['questions_answered']}, "
        f"questions_per_batch={session.get('questions_per_batch', 10)}"
    )

    if is_correct:
        result_text = "✅ *Correct!*\n\n"
    else:
        result_text = f"❌ *Incorrect.*\nCorrect answer: *{question.correct_answer}*\n\n"

    result_text += f"*Explanation:*\n{question.explanation}\n\n"
    result_text += f"Progress: {session['correct_answers']}/{session['questions_answered']} correct"

    keyboard = [[InlineKeyboardButton("Next Question", callback_data="next")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(result_text, reply_markup=reply_markup, parse_mode="Markdown")


async def show_explanation_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle explanation button click - show detailed explanation."""
    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id
    bot_instance = get_bot_instance()
    session = bot_instance.get_session(user_id)
    if not session or not session.get('current_question'):
        await query.edit_message_text("No active question.")
        return

    question = session['current_question']
    explanation_text = f"*Explanation:*\n{question.explanation}\n\n"
    explanation_text += f"*Correct Answer:* {question.correct_answer}"

    await query.edit_message_text(explanation_text, parse_mode="Markdown")


async def _show_next_question(query, user_id: int, bot_instance) -> None:
    """Helper function to show next question."""
    session = bot_instance.get_session(user_id)
    if not session:
        await query.edit_message_text("No active quiz session.")
        return

    # Check if we've reached the questions_per_batch limit
    questions_per_batch = session.get('questions_per_batch', 10)
    logger.info(
        f"Batch limit check: questions_answered={session['questions_answered']}, "
        f"questions_per_batch={questions_per_batch}, "
        f"will_end={session['questions_answered'] >= questions_per_batch}"
    )
    if session['questions_answered'] >= questions_per_batch:
        await query.edit_message_text(
            f"✅ *Session complete!*\n\n"
            f"Questions answered: {session['questions_answered']}\n"
            f"Correct: {session['correct_answers']}\n"
            f"Accuracy: {session['correct_answers']/session['questions_answered']*100 if session['questions_answered'] > 0 else 0:.1f}%\n\n"
            f"Use /topics to start a new quiz!",
            parse_mode="Markdown"
        )
        bot_instance.end_session(user_id)
        return

    repository = bot_instance.repository
    db_user = repository.get_user_by_telegram_id(user_id)

    # Get next question with unseen quota tracking and session exclusion
    question = repository.get_next_question(
        db_user.id,
        session['topic_id'],
        unseen_shown=session.get('unseen_shown', 0),
        unseen_target=session.get('unseen_target', 0),
        exclude_question_ids=session.get('shown_question_ids', [])
    )

    if not question:
        await query.edit_message_text(
            f"No more questions available for this topic!\n\n"
            f"Session complete!\n"
            f"Questions answered: {session['questions_answered']}\n"
            f"Correct: {session['correct_answers']}\n"
            f"Accuracy: {session['correct_answers']/session['questions_answered']*100 if session['questions_answered'] > 0 else 0:.1f}%\n\n"
            f"Use /topics to start a new quiz!",
            parse_mode="Markdown"
        )
        bot_instance.end_session(user_id)
        return

    # Track this question as shown in the session
    session['current_question'] = question
    session['start_time'] = datetime.utcnow()
    if 'shown_question_ids' not in session:
        session['shown_question_ids'] = []
    session['shown_question_ids'].append(question.id)

    # Check if this question was unseen and increment counter
    was_unseen = repository.is_question_unseen(db_user.id, question.id)
    if was_unseen:
        session['unseen_shown'] = session.get('unseen_shown', 0) + 1
        logger.info(
            f"Showing unseen question, progress: {session['unseen_shown']}/{session.get('unseen_target', 0)}"
        )

    # Shuffle answer choices to prevent answer position bias
    shuffled_choices, answer_mapping, correct_displayed = _shuffle_choices(question)
    session['answer_mapping'] = answer_mapping  # Store for answer validation
    session['correct_displayed'] = correct_displayed  # For logging purposes

    logger.debug(
        f"Answer shuffling: Original correct={question.correct_answer}, "
        f"Now displayed at={correct_displayed}, Mapping={answer_mapping}"
    )

    keyboard = [
        [InlineKeyboardButton("A", callback_data="answer:A")],
        [InlineKeyboardButton("B", callback_data="answer:B")],
        [InlineKeyboardButton("C", callback_data="answer:C")],
        [InlineKeyboardButton("D", callback_data="answer:D")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    question_text = f"*Question:*\n{question.question_text}\n\n"
    question_text += f"A: {shuffled_choices['A']}\n"
    question_text += f"B: {shuffled_choices['B']}\n"
    question_text += f"C: {shuffled_choices['C']}\n"
    question_text += f"D: {shuffled_choices['D']}\n"

    await query.edit_message_text(question_text, reply_markup=reply_markup, parse_mode="Markdown")


async def topic_stats_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle topic stats button click - show detailed stats for a specific topic."""
    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id
    topic_id = int(query.data.split(":")[1])

    logger.info(f"Topic stats {topic_id} requested by user {user_id}")

    bot_instance = get_bot_instance()
    repository = bot_instance.repository

    # Get topic
    topic = repository.get_topic(topic_id)
    if not topic:
        await query.edit_message_text("Topic not found.")
        return

    # Get user from database
    db_user = repository.get_user_by_telegram_id(user_id)
    if not db_user:
        await query.edit_message_text("User not found.")
        return

    # Get detailed topic stats
    stats = repository.get_user_stats(db_user.id, topic_id)

    # Format detailed statistics
    stats_text = f"📊 *{topic.name}*\n"
    stats_text += f"{'=' * 40}\n\n"

    stats_text += f"*Question Progress:*\n"
    stats_text += f"📚 Total Questions: {stats['total_questions']}\n"
    stats_text += f"👁 Questions Seen: {stats['questions_seen']}\n"
    stats_text += f"🆕 Not Yet Seen: {stats['questions_not_seen']}\n\n"

    stats_text += f"*Performance:*\n"
    stats_text += f"✅ Correct: {stats['total_correct']}\n"
    stats_text += f"❌ Incorrect: {stats['total_incorrect']}\n"
    stats_text += f"🎯 Accuracy: {stats['accuracy'] * 100:.1f}%\n\n"

    stats_text += f"*Learning Status:*\n"
    stats_text += f"⭐ Known: {stats['questions_known']}\n"
    stats_text += f"📖 Learning: {stats['questions_learning']}\n"
    stats_text += f"⏰ Due for Review: {stats['questions_due']}\n"

    if stats['average_response_time']:
        stats_text += f"\n*Speed:*\n"
        stats_text += f"⚡ Avg Response Time: {stats['average_response_time']:.1f}s\n"

    if stats['last_activity']:
        last_activity = stats['last_activity']
        if isinstance(last_activity, str):
            last_activity = datetime.fromisoformat(last_activity)
        stats_text += f"\n*Activity:*\n"
        stats_text += f"🕐 Last Practiced: {last_activity.strftime('%Y-%m-%d %H:%M')}\n"

    # Calculate progress percentage
    progress_pct = 0
    if stats['total_questions'] > 0:
        progress_pct = (stats['questions_known'] / stats['total_questions']) * 100

    stats_text += f"\n*Overall Progress:*\n"
    stats_text += f"📈 Mastery Level: {progress_pct:.1f}%\n"

    # Visual progress bar
    bar_length = 10
    filled = int(bar_length * progress_pct / 100)
    bar = "█" * filled + "░" * (bar_length - filled)
    stats_text += f"{bar} {progress_pct:.0f}%\n"

    # Back button
    keyboard = [[InlineKeyboardButton("« Back to All Stats", callback_data="stats:back")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(
        stats_text,
        parse_mode="Markdown",
        reply_markup=reply_markup
    )


async def stats_back_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle back button from topic stats - return to main stats menu."""
    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id
    logger.info(f"Stats back button clicked by user {user_id}")

    bot_instance = get_bot_instance()
    repository = bot_instance.repository

    # Get user from database
    db_user = repository.get_user_by_telegram_id(user_id)
    if not db_user:
        await query.edit_message_text("User not found.")
        return

    # Get overall stats
    stats = repository.get_user_stats(db_user.id)

    # Format overall statistics summary (same as stats_command)
    stats_text = f"📊 *Your Learning Statistics*\n\n"
    stats_text += f"📚 Total Questions: {stats['total_questions']}\n"
    stats_text += f"👁 Questions Seen: {stats['questions_seen']}\n"
    stats_text += f"🆕 Not Yet Seen: {stats['questions_not_seen']}\n\n"

    stats_text += f"✅ Correct: {stats['total_correct']}\n"
    stats_text += f"❌ Incorrect: {stats['total_incorrect']}\n"
    stats_text += f"🎯 Accuracy: {stats['accuracy'] * 100:.1f}%\n\n"

    stats_text += f"⭐ Known: {stats['questions_known']}\n"
    stats_text += f"📖 Learning: {stats['questions_learning']}\n"
    stats_text += f"⏰ Due for Review: {stats['questions_due']}\n"

    if stats['average_response_time']:
        stats_text += f"\n⚡ Avg Response Time: {stats['average_response_time']:.1f}s"

    if stats['last_activity']:
        last_activity = stats['last_activity']
        if isinstance(last_activity, str):
            last_activity = datetime.fromisoformat(last_activity)
        stats_text += f"\n🕐 Last Activity: {last_activity.strftime('%Y-%m-%d %H:%M')}"

    stats_text += "\n\n_Tap a topic below for detailed stats:_"

    # Create inline keyboard with topic buttons
    topics = repository.get_all_topics(active_only=True)
    keyboard = []

    for topic in topics:
        topic_stats = repository.get_user_stats(db_user.id, topic.id)
        if topic_stats['questions_seen'] > 0:
            # Show topic name with quick stats
            button_text = f"📘 {topic.name} ({topic_stats['questions_seen']}/{topic_stats['total_questions']})"
            keyboard.append([InlineKeyboardButton(
                text=button_text,
                callback_data=f"stats:{topic.id}"
            )])

    reply_markup = InlineKeyboardMarkup(keyboard) if keyboard else None

    await query.edit_message_text(
        stats_text,
        parse_mode="Markdown",
        reply_markup=reply_markup
    )
