import base64
import csv
import os
import random
import resend
from datetime import datetime

NO_MATCHES_TIPS = [
    "💡 Tip: Add more companies to increase your chances.",
    "💡 Tip: Check CONTRIBUTING.md to discover new companies.",
    "💡 Tip: Adjust your location keywords in config.yaml.",
]


def _score_emoji(fit_score):
    """Return emoji for fit score: 🔥 8+, ✨ 7+, 💡 below."""
    if fit_score >= 8:
        return "🔥"
    if fit_score >= 7:
        return "✨"
    return "💡"


def _get_banner_path():
    """Return path to assets/email-header.png, or None if not found."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    banner_path = os.path.abspath(os.path.join(script_dir, '..', 'assets', 'email-header.png'))
    return banner_path if os.path.exists(banner_path) else None


def send_email_digest(matched_jobs, companies_checked, config):
    """Send daily email digest with matched jobs, or no-matches summary if configured."""
    resend.api_key = os.getenv('RESEND_API_KEY')
    email_from = os.getenv('EMAIL_FROM', 'onboarding@resend.dev')
    email_to = os.getenv('EMAIL_TO')
    email_config = config.get('email', {})
    send_empty = email_config.get('send_if_no_matches', False)

    if not matched_jobs and not send_empty:
        return

    today = datetime.now().strftime('%Y-%m-%d')
    banner_path = _get_banner_path()
    banner_html = ''
    banner_attachment = None
    if banner_path:
        banner_html = '<img src="cid:banner" alt="Actually Remote" style="width: 100%; height: auto; display: block; vertical-align: top;" />'
        with open(banner_path, 'rb') as f:
            banner_attachment = {
                "filename": "email-header.png",
                "content": base64.b64encode(f.read()).decode('utf-8'),
                "content_id": "banner",
                "content_type": "image/png",
            }

    if not matched_jobs:
        subject = "Actually Remote — No matches today"
        total_companies = 0
        num_categories = 0
        try:
            with open('companies.csv', 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                rows = list(reader)
                total_companies = len(rows)
                categories = {r.get('category', '') for r in rows if r.get('category')}
                num_categories = len(categories)
        except (FileNotFoundError, KeyError):
            pass
        if total_companies and num_categories:
            monitoring_line = f"Monitoring {total_companies} companies across {num_categories} categories."
        elif total_companies:
            monitoring_line = f"Monitoring {total_companies} companies."
        else:
            monitoring_line = f"{companies_checked} companies checked today."
        tip = random.choice(NO_MATCHES_TIPS)
        html = f"""
<!DOCTYPE html>
<html>
<head><meta charset="utf-8"><title>{subject}</title></head>
<body style="font-family: system-ui, sans-serif; margin: 0; padding: 0;">
  {banner_html}
  <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
    <p style="color: #666;">{today}</p>
    <p>No new matches today. {companies_checked} companies checked.</p>
    <p style="color: #555;">Keep going — your next opportunity is being tracked.</p>
    <p style="color: #666; font-size: 14px;">{monitoring_line}</p>
    <p style="color: #888; font-size: 13px;">{tip}</p>
    <hr style="border: none; border-top: 1px solid #eee; margin: 24px 0;">
    <p style="color: #999; font-size: 12px;">Powered by Actually Remote</p>
  </div>
</body>
</html>
"""
    else:
        subject = f"Actually Remote — {len(matched_jobs)} new matches today"
        cards_html = []
        for job in matched_jobs:
            fit_score = job['fit_score']
            emoji = _score_emoji(fit_score)
            priority_tag = " [PRIORITY]" if job['is_priority'] else ""
            fit_analysis = job['fit_analysis']
            reasons_for = fit_analysis.get('reasons_for', [])[:2]
            reasons_against = fit_analysis.get('reasons_against', [])
            gap = reasons_against[0] if reasons_against else "None"

            reasons_for_html = "".join([f"<li>{r}</li>" for r in reasons_for])

            card = f"""
  <div style="border: 1px solid #eee; border-left: 4px solid #DBA11C;
              border-radius: 8px; padding: 16px; margin-bottom: 24px;
              background-color: #fafafa;">
    <p style="margin: 0 0 8px 0; font-size: 14px;">
      {emoji} <strong>{fit_score}/10</strong>{priority_tag} — {fit_analysis.get('recommendation', '')}
    </p>
    <p style="margin: 0 0 8px 0; font-size: 16px;">
      <a href="{job['url']}" style="color: #DBA11C;">{job['title']}</a>
    </p>
    <p style="margin: 0 0 12px 0; color: #666;">{job['company']}</p>
    <p style="margin: 0 0 4px 0; font-size: 14px;"><strong>✅ Good fit:</strong></p>
    <ul style="margin: 0 0 8px 0; padding-left: 20px;">{reasons_for_html}</ul>
    <p style="margin: 0; font-size: 14px;"><strong>⚠️ Gap:</strong> {gap}</p>
  </div>
"""
            cards_html.append(card)

        html = f"""
<!DOCTYPE html>
<html>
<head><meta charset="utf-8"><title>{subject}</title></head>
<body style="font-family: system-ui, sans-serif; margin: 0; padding: 0;">
  {banner_html}
  <div style="max-width: 600px; margin: 0 auto; padding: 24px 32px;">
    <p style="color: #666; margin-top: 0;">{today}</p>
{"".join(cards_html)}
    <hr style="border: none; border-top: 1px solid #eee; margin: 24px 0;">
    <p style="color: #999; font-size: 12px;">Powered by Actually Remote</p>
  </div>
</body>
</html>
"""

    try:
        params = {
            "from": os.getenv('EMAIL_FROM', 'onboarding@resend.dev'),
            "to": [os.getenv('EMAIL_TO')],
            "subject": subject,
            "html": html
        }
        if banner_attachment:
            params["attachments"] = [banner_attachment]
        resend.Emails.send(params)
        if matched_jobs:
            print(f"    ✅ Email digest sent ({len(matched_jobs)} matches)")
        else:
            print(f"    ✅ Email digest sent (no matches)")
    except Exception as e:
        print(f"    ❌ Failed to send email digest: {str(e)}")
