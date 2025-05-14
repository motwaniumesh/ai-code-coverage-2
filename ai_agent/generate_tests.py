import openai
import subprocess
import os

openai.api_key = os.getenv("OPENAI_API_KEY")

def get_coverage():
    subprocess.run(["coverage", "run", "-m", "pytest"], check=True)
    result = subprocess.run(["coverage", "report"], capture_output=True, text=True)
    for line in result.stdout.splitlines():
        if "TOTAL" in line:
            percent = int(line.strip().split()[-1].replace("%", ""))
            return percent
    return 100

def get_uncovered_lines():
    result = subprocess.run(["coverage", "report", "-m"], capture_output=True, text=True)
    return result.stdout

def generate_test_code(source_code, uncovered_info):
    prompt = f"""You are a Python developer.
Given this code:

{source_code}

And the following uncovered line info:

{uncovered_info}

Write a unit test using pytest that covers the missing parts.
"""
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

if __name__ == "__main__":
    coverage_percent = get_coverage()
    if coverage_percent >= 80:
        print(f"Coverage is {coverage_percent}%, no need to generate tests.")
        exit(0)

    print(f"Coverage is {coverage_percent}%, generating tests...")

    with open("src/my_module.py") as f:
        code = f.read()
    uncovered = get_uncovered_lines()

    test_code = generate_test_code(code, uncovered)

    os.makedirs("tests", exist_ok=True)
    with open("tests/test_my_module.py", "w") as f:
        f.write(test_code)

    print("Test generation complete.")
