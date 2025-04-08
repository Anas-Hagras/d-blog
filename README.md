# Blog Social Media Automation

This project automates the process of generating and publishing social media content for blog posts.

## Overview

The system consists of two main components:

1. **Extract Social Media Content**: A GitHub Action that runs when new blog posts are pushed to the repository. It detects new pages, generates social media content using AI, and creates a pull request with the generated content.

2. **Publish Social Media Content**: A GitHub Action that runs when a pull request with social media content is merged. It publishes the content to the appropriate social media platforms (currently X/Twitter).

## Folder Structure

```
.
├── _pages/                  # Blog posts in markdown format
├── scripts/                 # Python scripts for content generation and publishing
│   ├── social_media/        # Modular social media platform integrations
├── social_media/            # Generated social media content
│   └── <page-name>/         # Content for a specific blog post
│       └── X/               # Content for X (Twitter)
│           └── content.txt  # The actual content to be posted
└── .github/workflows/       # GitHub Actions workflows
```

## How It Works

### 1. Extract Social Media Content

When a pull request with new blog posts is merged to the main branch, the `extract-social-media.yml` workflow:

1. Detects **new** pages in the `_pages` directory that were **added** in the PR (not modified or deleted)
2. For each new page, generates social media content using OpenAI's API
3. Saves the content in the appropriate folder structure
4. Creates a new pull request with the generated content

### 2. Publish Social Media Content

When a pull request with social media content is merged, the `publish-social-media.yml` workflow:

1. Detects changes to social media content files that were added in the PR
2. Publishes the content to the appropriate social media platforms (currently X/Twitter)
3. Records the results of the publishing process

The workflow is designed to be a two-step process:

1. First PR: Add new blog post(s) → Merged → Triggers content generation → Creates second PR
2. Second PR: Contains generated social media content → When merged → Triggers publishing to social platforms

## Scripts

- `extract_social_media_content.py`: Generates social media content for a blog post
- `post_to_x.py`: Posts content to social media platforms (currently X/Twitter)
- `detect_new_pages.py`: Detects new pages in the repository

## Environment Variables

The following environment variables are required:

- `OPENAI_API_KEY`: API key for OpenAI
- `TWITTER_API_KEY`: API key for Twitter
- `TWITTER_API_SECRET`: API secret for Twitter
- `TWITTER_ACCESS_TOKEN`: Access token for Twitter
- `TWITTER_ACCESS_SECRET`: Access token secret for Twitter

## Architecture

The system has been refactored to support multiple social media platforms through a modular architecture:

1. **Platform Abstraction**: Each social media platform is implemented as a class that inherits from a common base class.
2. **Selective Publishing**: The system can now publish to specific platforms and only process specific files.
3. **Enhanced Results Handling**: Results of posting operations are now stored with more detailed information.

## Future Enhancements

The system is designed to be extensible to other social media platforms. To add support for a new platform:

1. Create a new platform class in the `scripts/social_media` directory
2. Update the `extract_social_media_content.py` script to generate content for the new platform
3. Update the `publish-social-media.yml` workflow to include the new platform

## Usage

### Manual Content Generation

To manually generate social media content for a blog post:

```bash
python scripts/extract_social_media_content.py _pages/your-blog-post.md X,LinkedIn,Instagram
```

### Manual Publishing

To manually publish social media content:

```bash
python scripts/post_to_x.py social_media
```

To publish specific files to specific platforms:

```bash
python scripts/post_to_x.py social_media posting_results.json "social_media/page1/X/content.txt,social_media/page2/X/content.txt" "X"
```
