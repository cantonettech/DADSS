# START HERE — Hosting DADSS/CCMS on Hostinger, Bluehost, or Any cPanel Host

This is the master checklist. Everything you need to put this system online
is already inside this folder — this page just tells you what each piece is
for and the order to use them in. Print this page or keep it open in a tab
while you work through cPanel. The steps are the same regardless of which
company sold you the hosting — Hostinger, Bluehost, GoDaddy, Namecheap,
HostGator, and most others all run cPanel, and cPanel is cPanel.

---

## 0. Before you start — what you need

- [ ] A hosting plan that shows **"Setup Python App"** in cPanel — this is
      usually a Business/Premium plan or higher, or any VPS/Dedicated plan,
      on Hostinger, Bluehost, GoDaddy, Namecheap, HostGator, or most other
      cPanel-based hosts. If you don't see it, you'll need to upgrade first
      — the system needs Python, not just PHP.
- [ ] Your domain or subdomain already pointed at your host (or one you
      plan to use, e.g. `dadss.yourdomain.com`).
- [ ] Your cPanel login (your host emails this when your hosting account is
      created, or find it under your host's account dashboard — often
      called "My Sites", "Manage", or similar).
- 15–20 minutes, uninterrupted.

You will **not** need: a terminal on your own computer, Git, Node.js, or any
programming knowledge. Everything below happens inside cPanel in a browser.

---

## 1. What's in this folder, and what it's for

| File / folder | What it's for | Do you touch it? |
|---|---|---|
| **`DEPLOYMENT.md`** | The full, detailed step-by-step hosting guide. **This is the main document — follow it top to bottom.** Everything else on this page just points into it. | Read it |
| **`database/ccms_demo_data.sql`** | A ready-made database — 6 communities, 6 contributors, and the admin/cashier logins, already set up. Import this via phpMyAdmin so you don't start from a blank system. | Upload via phpMyAdmin (step 1 below) |
| **`database/ccms_empty_schema.sql`** | The same database structure with **zero data** — for a genuinely clean real launch instead of the demo data above. Import this *instead of* the file above (not both). | Upload via phpMyAdmin (step 1 below) — pick one or the other |
| **`static/img/favicon.ico`, `robots.txt`, custom 400/403/404/500 pages** | Branded polish: the browser tab icon, a "don't index this private system" instruction for search engines, and proper DADSS-branded error pages instead of Django's generic ones. | Nothing — already wired up, no action needed |
| **`database/README.md`** | Exact click-by-click instructions for importing whichever of the two database files above you choose. | Read it |
| **`.env.example`** | A template for the settings that make this installation *yours* — your domain, your database password, your secret key. You copy this to a new file named `.env` and fill it in. | Copy → edit |
| **`passenger_wsgi.py`** | The technical file your host's cPanel server uses to start the app (works the same on Hostinger, Bluehost, or any other cPanel host). You don't edit this — just make sure it's uploaded. | Leave alone |
| **`requirements.txt`** | The list of software components the app needs. cPanel installs these automatically from this list — you just run one command. | Leave alone |
| **`README.md`** | Full project documentation and version history — useful background reading, not needed to get the site live. | Optional reading |

---

## 2. The five things you'll actually do in cPanel

Full detail for each of these is in **`DEPLOYMENT.md`** — this is just the
map so you know what's coming and roughly how long each part takes.

- [ ] **Step 1 — Database** *(5 min)*: cPanel → MySQL® Databases → create a
      database + user. Then cPanel → phpMyAdmin → Import → either
      `database/ccms_demo_data.sql` (with sample data) or
      `database/ccms_empty_schema.sql` (clean, no data) — pick one. *(See
      `database/README.md` for exact clicks.)*
- [ ] **Step 2 — Python App** *(3 min)*: cPanel → Setup Python App → Create
      Application, pointing at `passenger_wsgi.py`.
- [ ] **Step 3 — Upload the files** *(5 min)*: Upload everything in this
      folder into the Application root cPanel created for you in Step 2.
- [ ] **Step 4 — Configure `.env`** *(5 min)*: Copy `.env.example` to `.env`,
      fill in your domain, a new random secret key, and the database details
      from Step 1.
- [ ] **Step 5 — Install & launch** *(3 min)*: In Setup Python App's
      terminal: `pip install -r requirements.txt`, then
      `python manage.py collectstatic --noinput`, then click **Restart**.

Then visit your domain. You should see the login page.

---

## 3. First login

Whichever way you set up the database (imported the ready-made file, or
started empty and ran `createsuperuser` — both are covered in
`DEPLOYMENT.md`), your Super Administrator login is:

| | |
|---|---|
| **URL** | `https://yourdomain.com/accounts/login/` |
| **Username** | `admin` |
| **Password** | `ChangeMe123!` *(only if you imported the ready-made database — change this immediately after logging in, from Settings)* |

If you ran `createsuperuser` instead of importing the database, use whatever
username/password you set at that prompt.

---

## 4. If something doesn't work

`DEPLOYMENT.md` has a **Troubleshooting** section at the very bottom covering
the most common issues: blank/500 error pages, missing styling, "table
doesn't exist" errors, and the app not starting at all. Check there first —
it covers the same handful of things that trip up almost every shared-hosting
Django deployment.

---

## 5. After you're live

- [ ] Change the `admin` and `cashier1` passwords (Settings, or Users page).
- [ ] Turn on SSL (AutoSSL / SSL-TLS Status in cPanel) if it isn't already —
      `DEPLOYMENT.md` step 8.
- [ ] Decide whether to keep the 6 sample communities/contributors or replace
      them with real ones — either way is just normal use of the Communities
      and Contributors pages once you're logged in as Super Admin.
- [ ] Bookmark `DEPLOYMENT.md`'s "Updating the app later" section for next
      time you need to upload changes.
