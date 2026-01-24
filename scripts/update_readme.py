import requests
import re
from datetime import datetime, timezone

GITHUB_USERNAME = "joshkerr"
README_PATH = "README.md"


def get_github_join_date(username):
    """Fetch the GitHub account creation date."""
    response = requests.get(f"https://api.github.com/users/{username}")
    response.raise_for_status()
    data = response.json()
    return datetime.fromisoformat(data["created_at"].replace("Z", "+00:00"))


def calculate_membership_duration(join_date):
    """Calculate years, months, and days since joining."""
    now = datetime.now(timezone.utc)

    years = now.year - join_date.year
    months = now.month - join_date.month
    days = now.day - join_date.day

    if days < 0:
        months -= 1
        # Get days in previous month
        prev_month = now.month - 1 if now.month > 1 else 12
        prev_year = now.year if now.month > 1 else now.year - 1
        if prev_month in [1, 3, 5, 7, 8, 10, 12]:
            days_in_prev_month = 31
        elif prev_month in [4, 6, 9, 11]:
            days_in_prev_month = 30
        else:  # February
            if prev_year % 4 == 0 and (prev_year % 100 != 0 or prev_year % 400 == 0):
                days_in_prev_month = 29
            else:
                days_in_prev_month = 28
        days += days_in_prev_month

    if months < 0:
        years -= 1
        months += 12

    return years, months, days


def format_duration(years, months, days):
    """Format the duration as a human-readable string."""
    parts = []
    if years > 0:
        parts.append(f"{years} year{'s' if years != 1 else ''}")
    if months > 0:
        parts.append(f"{months} month{'s' if months != 1 else ''}")
    if days > 0:
        parts.append(f"{days} day{'s' if days != 1 else ''}")

    if len(parts) == 0:
        return "0 days"
    elif len(parts) == 1:
        return parts[0]
    elif len(parts) == 2:
        return f"{parts[0]} and {parts[1]}"
    else:
        return f"{parts[0]}, {parts[1]}, and {parts[2]}"


def update_readme(duration_text, join_date):
    """Update the README with the membership duration."""
    with open(README_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    # Pattern to match the GitHub stats section
    pattern = r"(<!-- GITHUB-STATS:START -->).*?(<!-- GITHUB-STATS:END -->)"

    join_date_str = join_date.strftime("%B %d, %Y")
    stats_section = f"""<!-- GITHUB-STATS:START -->
<img src="https://img.shields.io/badge/GitHub%20Member-{duration_text.replace(' ', '%20').replace(',', '%2C')}-blue?style=flat-square&logo=github" alt="GitHub Membership" />

*Member since {join_date_str}*
<!-- GITHUB-STATS:END -->"""

    if re.search(pattern, content, re.DOTALL):
        # Replace existing section
        new_content = re.sub(pattern, stats_section, content, flags=re.DOTALL)
    else:
        # Section doesn't exist, this shouldn't happen if README is set up correctly
        print("Warning: GITHUB-STATS markers not found in README")
        return

    with open(README_PATH, "w", encoding="utf-8") as f:
        f.write(new_content)

    print(f"Updated README with membership duration: {duration_text}")


def main():
    join_date = get_github_join_date(GITHUB_USERNAME)
    years, months, days = calculate_membership_duration(join_date)
    duration_text = format_duration(years, months, days)
    update_readme(duration_text, join_date)


if __name__ == "__main__":
    main()
