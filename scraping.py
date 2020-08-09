

try:
    profiles_urls = json.loads(request.form['profiles_urls'])
except json.JSONDecodeError:
    return 'ko'

try:
    linkedin_username = request.form['linkedin_username']
except KeyError:
    return 'ko'

try:
    linkedin_password = request.form['linkedin_password']
except KeyError:
    return 'ko'

s = Scraper(
    linkedin_username=linkedin_username,
    linkedin_password=linkedin_password,
    profiles_urls=profiles_urls
)

s.start()

return 'ok'