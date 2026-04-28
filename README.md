# BG3 Mod Tracker

A changelog tracker for Baldur's Gate 3 mods on **PC and console**. Automatically monitors the mod.io API every hour and shows what's new and what's been updated, grouped by date.

**[View the live site →](https://sherazfn.github.io/bg3-mod-tracker/)**

## Features

- 📦 Tracks **new mods** added to mod.io on any supported platform
- 🔄 Tracks **mod updates** — flagged whenever any platform's version bumps
- 🎮 Per-mod **platform badges** (PC / PS5 / XSX)
- 🔎 **Platform filter** chip (All / PC / Console), saved across visits
- 📅 Browse changes by date with easy navigation
- ⏰ Automatically checks for updates every hour
- 📱 Mobile-friendly responsive design

## How It Works

1. **Hourly Scrape** — A GitHub Action fetches the latest mod data from the mod.io API.
2. **History Tracking** — Changes are tracked using [git-history](https://github.com/simonw/git-history) to detect new and updated mods.
3. **HTML Generation** — A static HTML page is generated with the changelog.
4. **GitHub Pages** — The site is automatically deployed to GitHub Pages.

## Attribution

This project is a fork of [xKeeg/bg3-console-mod-tracker](https://github.com/xKeeg/bg3-console-mod-tracker) — original work by **xKeeg**. The upstream project tracks console mods only; this fork extends it to cover PC mods as well, adds a platform filter, and adjusts the UI/copy accordingly. All credit for the original design, scraping pipeline, and HTML generation goes to xKeeg.
