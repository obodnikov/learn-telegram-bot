"""Callback handlers for inline button interactions."""

from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from src.utils.logger import get_logger
from src.bot import get_bot_instance

logger = get_logger(__name__)


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
    selected_answer = query.data.split(":")[1]

    logger.info(f"Answer {selected_answer} selected by user {user_id}")

    bot_instance = get_bot_instance()
    session = bot_instance.get_session(user_id)
    if not session or not session.get('current_question'):
        await query.edit_message_text("No active question. Use /topics to start!")
        return

    question = session['current_question']
    is_correct = (selected_answer == question.correct_answer)

    response_time = None
    if session.get('start_time'):
        response_time = (datetime.utcnow() - session['start_time']).total_seconds()

    repository = bot_instance.repository
    db_user = repository.get_user_by_telegram_id(user_id)
    repository.update_progress(db_user.id, question.id, is_correct, response_time)

    session['questions_answered'] += 1
    if is_correct:
        session['correct_answers'] += 1

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

    repository = bot_instance.repository
    db_user = repository.get_user_by_telegram_id(user_id)
    question = repository.get_next_question(db_user.id, session['topic_id'])

    if not question:
        await query.edit_message_text(
            f"No more questions available!\n\n"
            f"Session complete!\n"
            f"Questions answered: {session['questions_answered']}\n"
            f"Correct: {session['correct_answers']}\n"
            f"Accuracy: {session['correct_answers']/session['questions_answered']*100 if session['questions_answered'] > 0 else 0:.1f}%"
        )
        bot_instance.end_session(user_id)
        return

    session['current_question'] = question
    session['start_time'] = datetime.utcnow()

    keyboard = [
        [InlineKeyboardButton("A", callback_data="answer:A")],
        [InlineKeyboardButton("B", callback_data="answer:B")],
        [InlineKeyboardButton("C", callback_data="answer:C")],
        [InlineKeyboardButton("D", callback_data="answer:D")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    question_text = f"*Question:*\n{question.question_text}\n\n"
    question_text += f"A: {question.choice_a}\n"
    question_text += f"B: {question.choice_b}\n"
    question_text += f"C: {question.choice_c}\n"
    question_text += f"D: {question.choice_d}\n"

    await query.edit_message_text(question_text, reply_markup=reply_markup, parse_mode="Markdown")
