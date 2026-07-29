from services.gemini import generate_answer

answer = generate_answer(
    "In one sentence, what is Retrieval-Augmented Generation?"
)

print(answer)