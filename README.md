# CCMS — Community Contribution Management System

A Django (function-based views) system for registering houses & contributors,
collecting contributions, auto-sending SMS receipts, and reporting — built with
Tailwind CSS, Bootstrap (modal/collapse components), Remixicon and vanilla
JavaScript/AJAX (no page reloads for CRUD).

## Latest changes (this round) — renamed the inner settings folder to fix a recurring "wrong folder" mistake

- **Root cause of "Could not open requirements file: ... requirements.txt"
  (when run locally, not on a host) identified**: the project's inner
  Django config folder was named `ccms/` — the *same name* as the outer
  extracted project folder. It's very easy to `cd` into that inner `ccms/`
  folder by mistake, thinking it's the project root, and then have
  `pip install -r requirements.txt` fail because `requirements.txt` is
  actually one level up.
- **Fixed by renaming the inner folder from `ccms/` to `config/`.** It now
  can't be confused with the outer project folder, whatever that's named
  (a downloaded zip often gets a name like `ccms_django_core_fixed (25)`
  from repeated downloads — `config/` never collides with that). This
  folder only ever contains `urls.py`, `wsgi.py`, `asgi.py`, and
  `context_processors.py` — there was never a reason to `cd` into it for
  any command; `manage.py`, `requirements.txt`, and `settings.py` all live
  one level up, at the actual project root.
- Updated every reference to the old `ccms.*` module paths —
  `ROOT_URLCONF`, `WSGI_APPLICATION`, and both context processor entries in
  `settings.py` — to `config.*`. `passenger_wsgi.py` needed no changes
  (it already referenced settings generically).
- **Verified nothing broke**: `manage.py check`, a full migration, the
  complete functional test suite (every module, every role), a real local
  server boot serving the login page, `passenger_wsgi.py` loading
  correctly, `check --deploy`, `collectstatic`, and the MySQL database path
  were all re-tested against the renamed structure — all clean.
- Updated the folder diagrams in `README.md` and `DEPLOYMENT.md` to show
  `config/` in place of the old `ccms/`, with an explicit note that it's
  not the folder to run commands from.

## Previous changes — removed Render.com support, back to a single, simple hosting path

- **Removed everything Render-specific**: `render.yaml`, `Procfile`,
  `build.sh`, `RENDER_DEPLOYMENT.md`, and `.python-version` are all gone.
  `settings.py` no longer parses a `DATABASE_URL` or trusts
  `*.onrender.com` hostnames. `requirements.txt` no longer includes
  `gunicorn`, `psycopg2-binary`, or `dj-database-url`.
- **This project now supports exactly one deployment path, thoroughly
  tested**: shared hosting via cPanel — Hostinger, Bluehost, GoDaddy,
  Namecheap, HostGator, and effectively any host offering cPanel's "Setup
  Python App" feature — using `passenger_wsgi.py` and MySQL, or SQLite for
  local development. See **`DEPLOYMENT.md`** for the full guide and
  **`INDEX.md`** as the quick-start checklist.
- Re-ran the full system after these removals to confirm nothing broke:
  `manage.py check` clean, `check --deploy` clean, the complete functional
  test suite (every module, every role) passing, and a real local server
  boot serving the login page successfully — all against the simplified
  settings.
- `settings.py` still lives at the project root (from the previous round) —
  that part of the layout is unchanged; only the Render-specific logic
  inside it was removed.

## Previous changes — real MySQL databases, favicon/robots.txt, branded error pages

- **Two real, verified MySQL databases** now ship in `database/`, not one:
  `ccms_demo_data.sql` (refreshed — 6 communities, 6 contributors, admin/
  cashier accounts) and a new `ccms_empty_schema.sql` (the identical table
  structure with zero rows, for a genuinely clean real launch instead of
  demo data). Both were produced by actually installing MySQL, running this
  project's real migrations against it, then test-importing each finished
  file into a fresh empty database afterward to confirm it loads cleanly —
  not just generated and assumed correct. `database/README.md` explains how
  to pick between the two.
- **Added the "public file" basics a professional deployment expects**: a
  branded favicon (matching the amber/navy DADSS mark) wired into every
  page and `/favicon.ico` directly, a `robots.txt` (this is a private
  internal system, so it tells search engines not to index it), and
  custom DADSS-branded 400 / 403 / 404 / 500 error pages in place of
  Django's generic ones — each triggered for real and checked in
  production mode (`DEBUG=False`), not just written and assumed to work.
- **Caught and fixed a real bug while testing the favicon redirect**: the
  first version resolved the static file's hashed production filename at
  server-startup time, before `collectstatic` had necessarily run yet —
  which would have crashed the entire site immediately in production.
  Found this by testing in production mode, not by inspection; fixed and
  re-verified.
- `INDEX.md` and `DEPLOYMENT.md` updated to walk through choosing between
  the demo and empty database files.
- Re-ran the full functional test suite (every module, every role) plus the
  new error-page checks — zero errors.

## Previous changes — self-hosted every frontend asset for reliable hosting anywhere

- **Removed every runtime dependency on public CDNs.** Previously, every page
  loaded Tailwind CSS, Bootstrap, Remixicon, and Chart.js live from
  `cdn.tailwindcss.com` / `cdn.jsdelivr.net`, and receipts additionally loaded
  QR-code/barcode libraries the same way. This is the most likely explanation
  for buttons or the sidebar "not looking right" — if a hosting network or
  browser blocks or is slow to reach an external CDN, the whole page can
  render unstyled, making a perfectly working button *look* broken. Worse,
  Tailwind's CDN script is explicitly not meant for production — it
  recompiles CSS in the visitor's browser on every single page load.
- **Every one of those is now compiled/bundled into the project's own
  `static/` folder** and served by Django itself (via WhiteNoise, already
  configured): a real production Tailwind build (scanned against the actual
  templates, ~36KB instead of a multi-hundred-KB runtime compiler), plus
  self-hosted Bootstrap, Remixicon (including its font files), Chart.js,
  the QR code and barcode libraries, and the Inter font the design already
  specified but never actually loaded. The page now renders identically and
  instantly whether the server has open internet access or not — important
  for shared hosting, where outbound network policy is sometimes limited.
- **Caught and fixed a real deployment-breaking bug this surfaced**:
  `collectstatic` — the command every deployment guide (including this one)
  tells you to run — initially failed outright, because a couple of the
  vendor files referenced a source-map / SVG-font file I hadn't included.
  On Bluehost, Hostinger, or anywhere else, this would have stopped a
  deployment cold with an unhelpful error. Fixed by testing `collectstatic`
  itself, with `DEBUG=False`, exactly as it will run in production — not
  just by testing the running app.
- **Re-verified the sidebar itself**: it was already built correctly as a
  vertical list (confirmed again in this pass) — the off-canvas mobile
  drawer from the previous round is untouched and still works the same way.
  If it ever visually looked "horizontal" or unclickable, the CDN issue
  above is the most likely cause, and should no longer occur now that
  nothing on any page depends on a public CDN being reachable.
- Re-ran the full functional test suite — including a true production-mode
  pass (`DEBUG=False`, hashed/versioned static filenames, real
  `collectstatic` output) covering login, every module, and every role —
  zero errors.
- Swapped in the newest set of development-pillar photos for the login page
  showcase (no other change needed — same filenames).

## Previous changes — expanded to 6 communities, fixed a real bug, everything re-verified

- **Expanded from 1 community/3 contributors to the 6 communities you asked
  for**, in this exact order: **1. Dome, 2. Agogo, 3. Asante Akim, 4. New
  Town, 5. Takoradi, 6. Nabikyire** — one house and one contributor seeded
  in each (6 contributors total). This zip's database ships pre-loaded with
  exactly this data; log in as `admin` / `ChangeMe123!` and you'll see it
  immediately. (I grouped all six under Dormaa Municipal, Bono Region for
  now, matching this scheme's home area — easy to correct per-community
  from Communities → Edit if any of them actually sit elsewhere.)
- **Added real, controllable ordering.** Communities used to always sort
  alphabetically with no way to change that. There's now a "Display Order"
  field (Communities → Edit), which is how the six communities above show
  up in your exact requested order everywhere in the system — lists,
  dropdowns, reports — instead of Agogo-before-Dome alphabetically.
- **Found and fixed a real bug this introduced**: my first pass made that
  new field required, which would have silently broken the "New Community"
  button (created via a modal that doesn't ask for it) with a 400 error.
  Caught it by re-running the full test suite, not by inspection — it's now
  optional and defaults sensibly.
- Rebuilt `seed_demo_data` to be safely re-runnable — running it again never
  duplicates anything — and added a `--reset` flag: run
  `python manage.py seed_demo_data --reset` against an existing database to
  archive any other active community (e.g. old leftover demo data) while
  guaranteeing these six exist. "Archive" here means the same thing it means
  everywhere else in CCMS — nothing is deleted, houses/contributors/payment
  history are preserved and restorable from Communities → View Archived.
- Re-ran the entire functional test suite (every create/edit/archive/
  restore/toggle/reminder/payment/report/export action, across every role)
  against the new data — zero errors, `check --deploy` still clean.

## Previous changes — fully responsive across phones, tablets and laptops

- **Fixed a real bug**: the sidebar had no mobile behavior at all — it was a
  fixed 256px column with no responsive classes, so on a phone it just sat
  there squeezing the page into a sliver next to it, and the "hamburger"
  button did nothing useful (it started from a visible state, not hidden).
  It's now a proper off-canvas drawer below the `lg` breakpoint (1024px):
  closed by default, slides in from the left over a dimmed backdrop when the
  menu button is tapped, closes on backdrop tap / the × button / picking a
  nav link / resizing past the breakpoint — and is the normal always-visible
  sidebar on laptop/desktop screens, exactly as before.
- **Every data table** (Communities, Houses, Contributors, Payments, Users,
  Audit Logs, the contributor payment ledger, dashboard's recent payments)
  now scrolls horizontally on narrow screens instead of squeezing columns
  into unreadable slivers — two tables (Users, Audit Logs) were missing this
  entirely and have been fixed.
- **Every two-column form** (create/edit Community, House, Contributor, User,
  Payment, Settings) now stacks into a single column on phones and pairs up
  into two columns from tablet width upward, so form fields and their labels
  never got cramped or truncated inside a modal on a small screen.
- Tightened header/content padding and made the notifications dropdown width
  adapt to the viewport so it can't run off the edge of a small phone screen.
- Re-ran the full functional test suite after these layout changes — nothing
  about how the system *works* changed, only how it *fits* each screen.

## Previous changes — rebranded to DADSS, login page redesigned with your photos

- **Renamed the system system-wide** to **Dormaa Akwamu Development Support
  Scheme (DADSS)**. Rather than hardcoding this in a few templates, I found
  the app already had an editable `site_name` field on the Settings page
  that wasn't actually wired to anything — so I connected it properly. The
  name now flows automatically into the browser tab title, sidebar,
  dashboard footer, login page, PDF report headers, and payment receipts.
  If a Super Admin renames it again later from Settings, it updates
  everywhere instantly — no code changes needed.
  (Note: you wrote "Schame" — I used "Scheme" since that's what the
  acronym DADSS stands for. Easy to change back if you meant it literally.)
- **Redesigned the login page** using the 7 development-pillar images you
  provided (Education, Health, Economic Development, Security, Environment,
  Infrastructure, Local Revenue Generation). On desktop, a dark showcase
  panel rotates through all 7 cards every 5 seconds with a smooth crossfade,
  soft shadow, and progress dots — shown as complete cards (not cropped)
  since each image already has its own title bar, border, and number badge
  designed in. The sign-in form itself was not touched functionally — same
  fields, same role selector, same "Forgot password" link. On mobile/tablet
  the photo panel hides and a compact DADSS header takes its place. The
  slideshow is decorative JavaScript only; the form works identically with
  JS disabled. Images were compressed from ~15MB to ~1.5MB total so the page
  still loads quickly.

## Previous changes — Super Admin price updates now carry debt forward + notify everyone by SMS

The **"Set Monthly Amount"** button on the Contributors page (Super Admin
only, purple button top-right) now does exactly what was asked for:

- Changing the monthly contribution amount **never erases what someone
  already owes (or is owed as a credit)**. Each contributor's current
  balance is frozen the instant the price changes and carried forward on
  top of the new amount. Example: a contributor who owed GH₵30 when the
  Super Admin raises the price from GH₵50 to GH₵100 now owes GH₵130
  (30 carried forward + the new GH₵100), not GH₵100 and not a
  recalculated lifetime total. A contributor with a GH₵30 *credit*
  similarly ends up owing GH₵70 (100 − 30), not GH₵100.
- **Every affected contributor gets an SMS immediately**, stating what
  they owed before, the new monthly amount, and their new balance —
  something like: *"Dear Ama, [Community] has updated the monthly
  contribution amount to GH₵100.00. You previously owed GH₵30.00. This
  has been added to the new amount, so your new balance is GH₵130.00."*
  This fires the moment the Super Admin confirms the change — not on a
  delay, not only for people who owe money, but for everyone the update
  applies to.
- Payments made *before* the price change stay counted against the old
  balance (already folded into the carried-forward amount); payments made
  *after* the change count against the new balance — so nothing is ever
  double-counted, no matter what day the change happens on.
- This can be applied system-wide, or scoped to a single community, from
  the same button/modal as before.
- The contributor detail page now shows, when relevant, how much of their
  "Total Expected" is carried-forward balance vs. new accrual, and
  separates "Total Paid" (since the current rate took effect) from
  lifetime total paid, so nothing looks like it silently vanished.

## Previous changes — verified working end-to-end, real password reset, security hardening

This build has now actually been **installed, migrated, and exercised
end-to-end** (every create/edit/archive/restore/toggle/reminder/payment/report
action, across every role) rather than just generated — the note below about
it never having been run no longer applies.

- **Generated the missing database migrations** — the project had model code
  but no migration files yet, so `migrate` had nothing to apply. Migrations
  for all seven apps are now included; `python manage.py migrate` works
  immediately on a fresh checkout.
- **"Forgot password" is now a real, working flow**, not a cosmetic stub. It
  looks up the account, generates a secure single-use token (Django's own
  password-reset token generator — same one Django's built-in reset view
  uses), and delivers a reset link via SMS to the phone number on file
  (through the existing `accounts/sms.py` gateway abstraction — swap
  `SMS_PROVIDER` for a real provider in production; `console` logs the link
  to the terminal for local testing). The link expires automatically and is
  invalidated the moment it's used or the password changes. The page always
  shows the same generic confirmation either way, so it can't be used to
  enumerate valid usernames/emails.
- **Security hardening in `settings.py`**: added `SESSION_COOKIE_HTTPONLY`,
  `SESSION_COOKIE_SAMESITE` / `CSRF_COOKIE_SAMESITE`,
  `SECURE_CONTENT_TYPE_NOSNIFF`, `X_FRAME_OPTIONS: DENY`,
  `SECURE_REFERRER_POLICY`, and HSTS/SSL-redirect settings that activate
  automatically in production (`DEBUG=False`). `python manage.py check
  --deploy` now passes cleanly with a real `SECRET_KEY` set.
- **Verified every clickable action actually works**: ran the full crawl of
  every page as every role (Super Admin, Administrator, Cashier, Auditor),
  and drove every AJAX action a button in the UI can trigger — create/edit
  modals, archive/restore, suspend/reactivate, payment recording + receipt
  printing + SMS resend, individual and bulk reminders, bulk pricing, CSV/
  Excel/PDF report exports, user management, audit log clearing — end to
  end, with zero server errors. Every `onclick` handler in the templates
  was confirmed to have a matching JavaScript function; no dead buttons
  were found.
- Included a ready-to-use `.env` (fresh, randomly generated `SECRET_KEY`,
  `DEBUG=True`, SQLite) so `python manage.py runserver` works immediately
  with zero setup. Use `.env.example` as the template for a real deployment
  instead.

## Previous changes — Cashiers can now see Contributors

- **Cashiers have the same Contributors access as Administrators** — they can
  now see the Contributors list (with payment status/balance for each
  person), open a contributor's full profile/payment breakdown, register new
  contributors, and send reminders — exactly what an Administrator can do
  there. Editing, deleting, suspending, and bulk-setting monthly amounts stay
  Super-Admin-exclusive, unchanged. The "Contributors" link now also appears
  in the Cashier's sidebar, and the dashboard's "Total Contributors" card now
  correctly links through for them too (previously a dead link for that role).

## Latest changes (previous round) — debt tracking, archiving instead of deleting, bulk pricing

- **Contribution debt/balance tracking** — every contributor now has a real
  running balance: `Total Expected` (monthly amount × months since
  registration) minus `Total Paid` = `Balance`. Pay less than expected (e.g.
  GH₵50 of a GH₵100 monthly amount) and the contributor shows **"Owing
  GH₵50.00"**; pay it all and they show **"Paid in Full"**; overpay and it's
  tracked as credit. This is computed live — nothing is hardcoded per month.
- **New Contributor Profile page** (click any contributor's name, or the eye
  icon) — full payment breakdown: Total Expected, Total Paid, Balance, a
  completion progress bar, and a chronological payment ledger showing the
  running balance *after every single payment* — exactly the "how is this
  contributor paying" analysis for reporting.
- **Bulk monthly amount setting** — Super Admin can set the monthly
  contribution amount for every contributor at once ("Set Monthly Amount" on
  the Contributors page), optionally scoped to one community. Individual
  amounts are still editable one at a time via the normal Edit form.
- **The payment page now shows a contributor's current balance** the moment
  they're selected, so the cashier can see at a glance whether they're
  catching up on arrears or paying ahead.
- **Suspend / Reactivate a contributor** — Super Admin only, one click, right
  on the Contributors list or their profile page.
- **"Default Monthly Amount" removed from Community** — pricing is now set
  per contributor (individually or in bulk), not inherited from the community.
- **Nothing is ever permanently deleted anymore — literally "keep every
  record."** Communities, Houses, and Contributors are now **archived**
  instead of hard-deleted: they disappear from active lists (archiving a
  community/house cascades to its houses/contributors too) but every row and
  **every single payment stays in the database forever** and can be restored
  by a Super Admin at any time via the new "View Archived" link. This also
  supersedes last round's payment-deleting force-delete — Payments were
  already permanently locked against edits/deletes at the model level; now
  nothing anywhere in the app can remove one, ever, for any role.

## Latest changes (previous round) — message preview, audit log/notification clearing, bug fixes

- **Fixed a real bug**: the "New Community" button had a leftover
  `data-modal-url` attribute left over from an earlier pattern, which caused a
  second, conflicting AJAX call to silently overwrite the just-opened create
  form with the communities table a moment later. Removed — "New Community"
  now reliably opens the create form and saves correctly.
- **Reminder messages are now previewed and editable before sending** — both
  the individual reminder icon and "Send Bulk Reminder" open a modal showing
  the exact SMS text that will go out. You can edit it, or clear it and write
  something completely new. The bulk version supports `{name}`, `{amount}`,
  and `{community}` placeholders that get substituted per contributor (or
  send the same literal text to everyone if you remove them).
- **Audit Logs: Super Admin can delete individual entries or clear everything**
  (optionally scoped to the current filter) — every other role can still view
  and export logs but cannot delete any of them.
- **Notifications can be cleared by Super Admin** — the bell dropdown pulls
  from the same Audit Log data, so a "Clear all" icon (Super-Admin-only) in
  the dropdown clears that underlying history.
- Did a full pass over every search feature in the app (global header search,
  Contributors/Houses/Communities/Payments/Users/Audit Logs list search, the
  payment page's contributor lookup) to confirm each one queries correctly
  end to end.

## Latest changes (previous round) — Super Admin authority + reporting upgrades

- **Fixed the delete error** you hit ("payment history exists for this
  contributor"): **Super Administrators can now delete anything, unconditionally**
  — Communities, Houses, and Contributors — even when payment history is linked.
  Deleting cascades sensibly (e.g. deleting a house also removes its
  contributors and their payments) and every force-delete is recorded in the
  Audit Log with exactly what was removed.
- **Permission model tightened system-wide**: only the **Super Administrator**
  can edit or delete existing records anywhere in the system now (Communities,
  Houses, Contributors — Users and Settings already worked this way). Every
  other role — Administrator included — can still *view* and *create* new
  records (register a house, register a contributor, receive a payment) but
  can no longer edit or delete anything. Edit/Delete icons are hidden from the
  UI for anyone who isn't a Super Admin, so there's nothing clickable that
  would just error out.
- **Reports now always show the total amount** — every report with a monetary
  column (Daily, Monthly, Yearly, Community, Collector, House, Outstanding)
  displays a bold **TOTAL** row on-screen and in every exported file.
- **Excel and PDF export added** — the Reports page's Export button is now a
  dropdown: **CSV, Excel, or PDF**, your choice, each formatted (colored
  header row, bold total row) rather than a plain data dump.
- **Auditors can generate reports** (already true from an earlier round —
  confirmed still working with the new export formats).
- **Super Admin already sees everything** — Cashier is the only role whose
  dashboard/reports/payment list are scoped to their own activity; Super
  Admin, Administrator, and Auditor views were never filtered, so the Super
  Admin already has full visibility into what every cashier, administrator,
  and auditor is doing system-wide.

## Latest changes (previous round) — visual redesign to match the provided mockup

- **Sidebar**: rebuilt as a dark navy panel (matches the reference design's color),
  with the exact nav item set/order from the mockup: Dashboard, Registrations,
  Contributors, Payments, Communities, Reports, Analytics, Notifications, Settings,
  Users, Audit Logs. "Notifications" opens the same live activity dropdown as the
  header bell. **Audit Logs is a new page** (Super Admin + Auditor) backed by the
  existing AuditLog model — filterable by action type and searchable.
- **Header**: added a functional global search bar (searches contributors, houses,
  and payments in one go — try a name, phone number, house number, or receipt
  number) and a proper avatar dropdown (name + role, with a Settings/Logout menu).
- **Dashboard**: redesigned to match the mockup — KPI cards with colored icon
  squares (blue/green/purple/orange) and live month-over-month growth percentages,
  a "Collection Overview" line chart with a This Year/6mo/3mo period switch, a
  "Contributions by Community" donut with a color-coded legend, a restyled
  "Recent Contributions" table, and a new **Contribution Status** widget showing
  live Paid / Pending / Overdue breakdowns (Overdue is computed from each
  contributor's last payment date vs. the "Overdue After" setting in System
  Settings).
- Note: the mockup's phone "Thank You" screen, WhatsApp bubble, and the bottom
  marketing panels ("Core Features", "What You Need", etc.) are pitch/presentation
  content rather than actual app screens, so they weren't rebuilt as literal UI —
  the equivalent real functionality (payment confirmation, SMS receipts) already
  exists on the receipt page and via the SMS system.

## Previous round's changes

- Removed the "House GPS Address" field from house registration entirely.
- Super Admins can now force-delete a house that still has linked contributors
  (payment history is still always protected, for every role).
- Login page redesigned — simpler, more professional layout, with a role
  selector (Super Admin / Administrator / Cashier / Auditor). Logging in now
  cross-checks the selected role against the account's real role.
- Receipts and reports now show explicit **Date** and **Time** columns (data
  was always captured to the second — this makes it easier to read at a glance).
- Payment capture: selecting **Mobile Money** or **Bank Transfer** now reveals
  Account Number + Account Holder Name fields (required for those two methods).
- Cashiers can now access **Reports** (scoped to their own collections —
  nothing about another cashier's activity is exposed).
- The app is now ready to deploy on **Hostinger or Bluehost** shared hosting
  via cPanel's "Setup Python App" (Passenger) — see **DEPLOYMENT.md**.

## What's included (Phase 1 core + full interactivity pass + reminders)

- Branded footer on every page: "Developed by Cantonet Technologies"
- Custom `User` model with UUID PK and 4 roles: Super Administrator, Administrator, Cashier, Auditor
- Role-based access control (`accounts/decorators.py`) — every nav link, button and icon is
  gated to match the exact role matrix from the spec (e.g. only Super Admin manages users/settings;
  Auditor gets read-only access to payment history & reports; Cashier never sees edit/delete)
- **Communities** — full CRUD via AJAX modals; can also be created inline (see Houses below)
- **Houses** — full CRUD, house number + digital address, searchable. The **Community** field
  is now a type-in field (with autocomplete of existing names) instead of a dropdown — typing a
  new name creates that community on the fly, no need to leave the form. **GPS Latitude/Longitude
  have been merged into one field, "House GPS Address"**.
- **Contributors** — full CRUD, photo upload, community→house cascading dropdown,
  search by **name, house address, or phone number**
- **Payments** — contributor search & auto-fill, amount capture, **locked forever
  after save** (enforced at the model level), automatic receipt number, automatic SMS
  receipt on save, printable receipt with QR code + barcode, admin-only reprint,
  and a **Retry SMS** button for any receipt whose SMS failed to send
- **Dashboard** — every KPI card is a clickable link into the relevant filtered page/report;
  recent-payment rows link straight to their receipt
- **Analytics** (`/analytics/`) — contribution growth (12mo), top communities, top collectors,
  payment methods, payment rate, average/highest/lowest contribution, month-over-month and
  year-over-year comparison — all real charts backed by live data
- **Reports** (`/reports/`) — Daily / Monthly / Yearly / Community / Collector / House /
  Outstanding-Payments / SMS reports, each filterable and **exportable to CSV** with one click
  (no extra dependency needed — uses Python's built-in `csv` module)
- **System Settings** (`/accounts/settings/`, Super Admin only) — editable site name, currency
  symbol, SMS provider + sender ID, low-collection alert threshold, overdue-reminder window
- **User management** (Super Admin only) — create, edit (role/community/contact info),
  suspend/reactivate, and delete users, all via the same AJAX-modal pattern as everything else
- **Reminder messaging** — send a payment reminder SMS to a single contributor (message icon
  on each row) or to every contributor matching the current search/filter in one click
  ("Send Bulk Reminder" on the Contributors page)
- **Notification bell** — a real dropdown pulling the 10 most recent audit-log events
  (logins, payments, edits, deletes, SMS, exports) via `/accounts/notifications/api/`
- Every prompt/alert/confirm uses a **custom Bootstrap modal** — no native
  browser `alert()`/`confirm()` anywhere, and **every button/icon in the UI is wired to a
  real handler** (no dead `href="#"` links remain)
- UUID primary keys on every model
- Audit log (login, logout, create, edit, delete, payment, sms, export)
- SMS is provider-agnostic (`accounts/sms.py`) — defaults to console logging in
  dev; swap in Arkesel/Hubtel/Twilio/Africa's Talking credentials for production

## Not yet built (next iterations)

Excel/PDF export (CSV is implemented), bulk Excel import, WhatsApp/2FA, offline sync,
mobile money integration, "Collection Target" / forecast charts.

## Setup (local development)

No `.env` file is required for local dev — every setting has a safe default
(SQLite, DEBUG=True, console SMS). Create one only if you want to override
something; see `.env.example`.

```bash
cd ccms
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

pip install -r requirements.txt

python manage.py makemigrations accounts communities houses contributors payments reports
python manage.py migrate

# Optional: seed a demo community, houses, contributors, and a super admin
python manage.py seed_demo_data
# -> creates username: admin / password: ChangeMe123!
# -> creates username: cashier1 / password: ChangeMe123!

# Or create your own super admin instead:
python manage.py createsuperuser

python manage.py runserver
```

Then visit **http://127.0.0.1:8000/** and log in.

## Deploying to Hostinger / Bluehost (or any cPanel host)

See **DEPLOYMENT.md** for the full step-by-step guide. In short: this project
now includes `passenger_wsgi.py` (cPanel's "Setup Python App" entry point),
environment-variable-driven settings (`.env.example`), Whitenoise for static
files, and optional MySQL support (`PyMySQL`) — no code changes needed
between local dev and shared hosting, only environment variables.

Every CSS/JS library the UI needs (Tailwind, Bootstrap, Remixicon, Chart.js,
the QR-code/barcode libraries used on receipts, and the Inter font) is
already compiled/vendored into `static/` — there's nothing to build and no
Node.js needed on the host. `collectstatic` (see above) is the only static-
asset step a deployment ever needs to run.

You only need Node.js if you plan to change which Tailwind *classes* are
used in the templates (adding a new one that wasn't there before) — the
compiled `static/css/tailwind.css` only contains classes the build actually
found in use. The config to do this is already included in `frontend-build/`:
```bash
cd frontend-build
npm install tailwindcss@3
npx tailwindcss -i ./input.css -o ../static/css/tailwind.css --minify
```
That's it — `tailwind.config.js` (the color/font theme) and `input.css`
(the standard three `@tailwind` directives) are both already there.

## Project layout

```
manage.py
settings.py            # Django settings — lives at the project root
config/                # urls.py, wsgi.py, asgi.py, context_processors.py (NOT the project root — don't cd into this)
accounts/               # Custom User, roles, login/logout, audit log, SMS helper, settings, notifications
communities/            # Community model + CRUD
houses/                 # House model + CRUD (+ digital address, GPS)
contributors/            # Contributor model + CRUD (+ photo, search)
payments/               # Payment model (locked on save) + capture/receipt/SMS-retry flow
dashboard/               # KPI dashboard + analytics page
reports/                 # Filterable reports + CSV export
templates/               # Tailwind/Bootstrap/Remixicon templates, AJAX partials
static/js/main.js        # Modal system, toasts, live search, delete-confirm, notification bell
static/css/custom.css
```

## Notes on the "locked payment" rule

`payments/models.py::Payment.save()` raises `ValidationError` on any attempt to
resave an existing payment, and `Payment.delete()` always raises. There is
intentionally no `payment_update` or `payment_delete` view — the UI never
offers edit/delete controls on payments, only "View Receipt" and (for
admins) "Reprint".

## Swapping in a real SMS provider

Edit `settings.py` (at the project root, alongside `manage.py`):
```python
SMS_PROVIDER = 'arkesel'   # or 'hubtel' / 'twilio' / 'africastalking'
SMS_API_KEY = 'your-key-here'
```
Then implement the actual HTTP call for that provider inside `accounts/sms.py::send_sms()`.
