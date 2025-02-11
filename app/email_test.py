import resend

resend.api_key = "re_3zxGBYy6_MU5yTwwrLhmpbq4u8bMTTgxu"  # Replace with your actual Resend API key

r = resend.Emails.send({
    "from": "lucas@qwiknotes.com",  # Use this or your verified email
    "to": "lucas@weaverschool.com",  # Replace with your email
    "subject": "Hello World",
    "html": "<p>Congrats on sending your first email!</p>"
})

print(r)