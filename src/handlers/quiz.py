"""Quiz interaction handlers for managing quiz sessions."""

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


async def next_question_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Show next question in quiz session.

    Args:
        update: Telegram update object
        context: Callback context
    """
    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id
    bot_instance = get_bot_instance()
    session = bot_instance.get_session(user_id)
    if not session:
        await query.edit_message_text(
            "No active quiz session. Use /topics to start one!"
        )
        return

    # Check if we've reached the questions_per_batch limit
    questions_per_batch = session.get('questions_per_batch', 10)
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

    # Get next question using spaced repetition with unseen quota tracking and session exclusion
    repository = bot_instance.repository
    db_user = repository.get_user_by_telegram_id(user_id)

    question = repository.get_next_question(
        db_user.id,
        session['topic_id'],
        unseen_shown=session.get('unseen_shown', 0),
        unseen_target=session.get('unseen_target', 0),
        exclude_question_ids=session.get('shown_question_ids', [])
    )

    if not question:
        await query.edit_message_text(
            f"No more questions available for '{session['topic_name']}'!\n\n"
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

    # Create answer buttons
    keyboard = [
        [InlineKeyboardButton("A", callback_data=f"answer:A")],
        [InlineKeyboardButton("B", callback_data=f"answer:B")],
        [InlineKeyboardButton("C", callback_data=f"answer:C")],
        [InlineKeyboardButton("D", callback_data=f"answer:D")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Format question text
    question_text = f"*Question:*\n{question.question_text}\n\n"
    question_text += f"A: {shuffled_choices['A']}\n"
    question_text += f"B: {shuffled_choices['B']}\n"
    question_text += f"C: {shuffled_choices['C']}\n"
    question_text += f"D: {shuffled_choices['D']}\n"

    await query.edit_message_text(
        question_text,
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )
