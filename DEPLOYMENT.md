# Deploying CCMS to Hostinger, Bluehost, or Any cPanel Host

Most shared-hosting providers — Hostinger, Bluehost, GoDaddy, Namecheap,
HostGator, A2 Hosting, and many others — run **cPanel**, and cPanel's
**"Setup Python App"** feature (on Business/Premium plans and above, and on
all VPS plans) is what this project is built for. That feature runs Django
through **Passenger**, which is what `passenger_wsgi.py` at the project
root is for. The steps below work the same way regardless of which company
resells the hosting — cPanel is cPanel.

> **If your plan doesn't show "Setup Python App" in cPanel**, your hosting
> tier doesn't support Python — you'd need to upgrade to a plan that does,
> or choose hosting that explicitly advertises Python/Django support.

## 1. Create the database

1. In cPanel, open **MySQL® Databases**.
2. Create a database (e.g. `ccms`) — cPanel will prefix it with your account
   username automatically, e.g. `yourusername_ccms`.
3. Create a database user with a strong password, and add that user to the
   database with **All Privileges**.
4. Note the full database name, username, and password — you'll need them
   for `.env` in step 4.
5. **Optional shortcut**: this project ships with two ready-made database
   files in `database/` — `ccms_demo_data.sql` (6 communities, 6
   contributors, and admin/cashier accounts already in it) and
   `ccms_empty_schema.sql` (the same tables, completely empty, for a clean
   real launch). Import **one of the two** via phpMyAdmin (see
   `database/README.md` for the exact steps) and you can skip running
   `migrate` later in step 6. Otherwise, leave the database empty and step 6
   will build it from scratch.

## 2. Create the Python App

1. In cPanel, open **Setup Python App**.
2. Click **Create Application**.
3. Set:
   - **Python version**: the highest 3.10+ available.
   - **Application root**: a folder outside `public_html`, e.g. `ccms_app`
     (keeps your source code from being directly web-accessible).
   - **Application URL**: your domain or subdomain (e.g. `yourdomain.com`).
   - **Application startup file**: `passenger_wsgi.py`
   - **Application Entry point**: `application`
4. Click **Create**. cPanel will show you an activation command like:
   ```
   source /home/yourusername/virtualenv/ccms_app/3.11/bin/activate && cd /home/yourusername/ccms_app
   ```
   Keep this handy — you'll run it before any `pip`/`manage.py` command below.

## 3. Upload the project

Upload the contents of this zip into the **Application root** folder you set
above (via cPanel File Manager's Upload+Extract, or `git clone` / `scp` if
you have SSH access — Hostinger Business+ and Bluehost VPS both offer SSH).

The folder should end up looking like:
```
ccms_app/
├── manage.py
├── settings.py
├── passenger_wsgi.py
├── requirements.txt
├── config/            # urls.py, wsgi.py, asgi.py — NOT the project root, don't cd into this for commands
├── accounts/  communities/  houses/  contributors/  payments/  dashboard/  reports/
├── templates/  static/  media/
```

## 4. Configure environment variables

Copy `.env.example` to `.env` inside the Application root and fill in real
values — especially `SECRET_KEY` (generate a random 50-character string),
`ALLOWED_HOSTS` (your domain), and the `DB_*` values from step 1:

```bash
cp .env.example .env
nano .env   # or edit via cPanel File Manager
```

Set `DB_ENGINE=mysql` so the app uses the MySQL database you created instead
of SQLite (SQLite works but MySQL is the safer choice on shared hosting —
some hosts periodically reset writable directories, which can wipe a SQLite
file).

## 5. Install dependencies

Back in **Setup Python App**, scroll to your app and click the terminal
icon (or run the activation command from step 2 over SSH), then:

```bash
pip install -r requirements.txt
```

## 6. Run migrations and collect static files

Still inside the activated environment:

```bash
python manage.py collectstatic --noinput
```

**If you imported one of the two files from `database/` in step 1**, the
database already has its tables — skip the `migrate` command below.
- Imported `ccms_demo_data.sql`? You're fully ready — skip straight to step 7.
- Imported `ccms_empty_schema.sql`? Run `python manage.py createsuperuser`
  below to create your first login, then skip to step 7.

Otherwise (empty database, nothing imported), build it from scratch now:

```bash
python manage.py migrate
python manage.py seed_demo_data   # optional — creates a demo super admin + sample data
# or, to make your own super admin instead:
python manage.py createsuperuser
```

## 7. Restart the app

In **Setup Python App**, click **Restart** on your application. Visit your
domain — you should see the CCMS login page.

## 8. Point your domain / SSL

- If the Application URL you set in step 2 was a subdomain, make sure its
  DNS/domain mapping is correct in cPanel's **Domains** section.
- Enable **AutoSSL** (Hostinger) or the **SSL/TLS Status** tool (Bluehost) so
  the site is served over HTTPS — required for `SESSION_COOKIE_SECURE` and
  `CSRF_COOKIE_SECURE` (both default to `True` automatically once `DEBUG=False`).

## Updating the app later

```bash
# activate the virtualenv (see step 2's activation command), then:
git pull   # or re-upload changed files
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
# then click Restart in Setup Python App
```

## Media uploads (contributor photos, community logos)

`MEDIA_ROOT` defaults to a `media/` folder inside the Application root. On
shared hosting this is fine for moderate use; if storage becomes a concern,
point `MEDIA_ROOT` at a folder under `public_html` instead (or migrate to S3
using `django-storages` later — not included in this build).

## Troubleshooting

- **500 error, nothing else**: set `DEBUG=True` temporarily in `.env`, reload
  the page to see the real traceback, then set it back to `False`.
- **Static files (CSS/icons) missing**: re-run `collectstatic` and confirm
  `whitenoise` installed correctly (`pip show whitenoise`).
- **"Table doesn't exist" errors**: `python manage.py migrate` wasn't run, or
  ran against the wrong database — double-check `.env`'s `DB_*` values.
- **Passenger won't start the app**: check the app's error log link in
  **Setup Python App** — it usually points straight at the Python exception.
