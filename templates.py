"""
templates.py
Built-in prompt templates for Orbit. Each template maps a label to
a prompt prefix that gets inserted into the chat input for the user to complete.
"""

BUILTIN_TEMPLATES = {
    "Summarize Text": "Summarize the following text in a concise paragraph, capturing the key points:\n\n",
    "Explain Code": "Explain what the following code does, step by step, in plain language:\n\n",
    "Generate Ideas": "Generate 10 creative ideas for the following topic:\n\n",
    "Rewrite Content": "Rewrite the following content to improve clarity and flow, keeping the original meaning:\n\n",
    "Translate": "Translate the following text into English (or specify a target language):\n\n",
    "Create Email": "Write a professional email about the following:\n\n",
    "Brainstorm": "Brainstorm possible approaches and solutions for the following problem:\n\n",
}

TEMPLATE_ICONS = {
    "Summarize Text": "📝",
    "Explain Code": "💻",
    "Generate Ideas": "💡",
    "Rewrite Content": "✍️",
    "Translate": "🌐",
    "Create Email": "📧",
    "Brainstorm": "🧠",
}
