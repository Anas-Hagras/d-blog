# Email Subscription System

This document explains how to use the email subscription system for your blog, which integrates Resend for email delivery and Supabase for subscriber management.

## Overview

The subscription system consists of two main components:

1. **Supabase Backend**: Manages subscriber data storage and provides subscription/unsubscription endpoints
2. **Resend Integration**: Handles email formatting and delivery to subscribers

When you publish a new blog post, the system automatically:

1. Detects the new post
2. Generates email content using AI
3. Fetches active subscribers from Supabase
4. Sends personalized emails to each subscriber via Resend
5. Tracks delivery results

## Supabase Setup

### Database Configuration

The system uses a Supabase database table called `email_subscribers` with the following structure:

| Column     | Type      | Description                          |
| ---------- | --------- | ------------------------------------ |
| id         | uuid      | Primary key, automatically generated |
| email      | text      | Subscriber's email address (unique)  |
| active     | boolean   | Subscription status (true = active)  |
| created_at | timestamp | When the subscriber was added        |

To create this table in your Supabase project:

1. Log in to your [Supabase dashboard](https://app.supabase.com)
2. Select your project
3. Go to the SQL Editor
4. Run the following SQL:

```sql
CREATE TABLE email_subscribers (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  email TEXT UNIQUE NOT NULL,
  active BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create an index for faster lookups
CREATE INDEX email_subscribers_email_idx ON email_subscribers(email);
```

### Edge Function Deployment

The system includes a Supabase Edge Function (`email_subscriptions`) that handles subscription and unsubscription requests. To deploy it:

1. Install the Supabase CLI if you haven't already:

   ```bash
   npm install -g supabase
   ```

2. Log in to Supabase:

   ```bash
   supabase login
   ```

3. Link your local project to your Supabase project:

   ```bash
   supabase link --project-ref your-project-ref
   ```

4. Deploy the function:
   ```bash
   supabase functions deploy email_subscriptions --use-api
   ```

The function provides two endpoints:

- `POST /functions/v1/email_subscriptions` - For subscribing (accepts JSON with an email field)
- `GET /functions/v1/email_subscriptions/unsubscribe?id=<subscriber_id>` - For unsubscribing

### Function Configuration

The Edge Function is configured in `supabase/config.toml`:

```toml
[functions.email_subscriptions]
enabled = true
verify_jwt = false
import_map = "./functions/email_subscriptions/deno.json"
entrypoint = "./functions/email_subscriptions/index.ts"
```

The function uses Deno and is written in TypeScript. The import map is defined in `supabase/functions/email_subscriptions/deno.json`.

## Resend Setup

1. Sign up for a [Resend](https://resend.com) account
2. Get your API key from the Resend dashboard
3. Add the following to your `.env` file:
   ```
   RESEND_API_KEY="your_api_key_here"
   RESEND_FROM_EMAIL="your-email@yourdomain.com"
   BLOG_BASE_URL="https://yourblog.com"  # Used for constructing post URLs in emails
   ```
4. Set up your Supabase credentials in the `.env` file:
   ```
   SUPABASE_URL="https://your-project-id.supabase.co"
   SUPABASE_SERVICE_ROLE_KEY="your-service-role-key"
   SUPABASE_SUBSCRIBE_FUNCTION_URL="https://your-project-id.functions.supabase.co/email_subscriptions/unsubscribe"  # Optional, will be constructed from SUPABASE_URL if not provided
   ```

## Managing Subscribers

Subscribers are managed through the `scripts/manage_subscribers.py` script, which interacts with the Supabase database.

### Basic Commands

```bash
# List all active subscribers
python scripts/manage_subscribers.py list

# List all subscribers (including inactive)
python scripts/manage_subscribers.py list --all
```

## Subscription Flow

1. **User Subscribes**:

   - User submits their email through a form on your website
   - The form sends a POST request to the Supabase Edge Function
   - The function validates the email and adds it to the database
   - A confirmation message is returned to the user

2. **Sending Emails**:

   - When a new blog post is published, the system generates email content
   - The `ResendPlatform` class fetches active subscribers from Supabase
   - It sends personalized emails to each subscriber with unique unsubscribe links
   - Results are tracked and reported

3. **User Unsubscribes**:
   - Each email contains a personalized unsubscribe link
   - When clicked, it sends a request to the Supabase Edge Function
   - The function removes the subscriber from the database
   - A confirmation message is displayed to the user

## Email Content and Customization

### Email Template

The HTML email template is stored in `templates/email/blog_post.html`. You can modify this file to customize the email appearance and layout. The template uses the following placeholders:

- `{{title}}`: The title of the blog post
- `{{content}}`: The content of the blog post (generated by the AI)
- `{{publish_date}}`: The publication date of the blog post
- `{{post_url}}`: The URL to the full blog post
- `{{unsubscribe_url}}`: A personalized URL for unsubscribing from the newsletter

The template is loaded dynamically when sending emails, so changes to the template will take effect immediately without requiring code changes. The template includes responsive styling for optimal viewing on various devices.

### Email Content Generation

The content for emails is generated using the prompt in `prompts/Resend.txt`. This prompt instructs the AI to:

1. Generate a compelling subject line (which will be used as the email subject)
2. Create engaging content that will be inserted into the `<div id="content">` section of the template

The prompt is designed to work with the template, ensuring that the AI generates content that fits well within the email structure. The AI is aware of the template structure and will generate content accordingly.

When the AI generates content, it starts with a subject line in the format:

```
SUBJECT: Your compelling subject line here
```

This subject line is automatically extracted and used as the email subject. The rest of the generated content is inserted into the `{{content}}` placeholder in the template.

### Blog Post Data Extraction

The system automatically extracts metadata from your blog posts, including:

- Title: Used as the email subject if no subject line is provided
- Publish date: Displayed in the email
- Category: Used for constructing the post URL

### Content Types

The Resend platform supports three different content types:

1. **Markdown (default)**: The LLM generates Markdown content, which is converted to HTML using a Markdown parser with support for tables, code highlighting, and other extensions.
2. **Plain Text**: The LLM generates plain text content, which is converted to HTML by replacing newlines with `<br>` tags.
3. **HTML**: The LLM generates HTML content directly, which is inserted into the template as-is.

To specify the content type when sending an email, use the `content_type` parameter in the `post_content` method:

```python
# Example: Send content as markdown
resend_platform.post_content(
    content=markdown_content,
    page_name="My Blog Post",
    content_type="markdown"
)
```

If no content type is specified, the default is "markdown".

### Media Attachments

The system automatically detects and attaches media files to your emails. Supported image formats include:

- JPG/JPEG
- PNG
- GIF

Media files can be placed in either:

- The platform folder (e.g., `social_media/your-post-name/Resend/image.jpg`)
- The version-specific folder (e.g., `social_media/your-post-name/Resend/v1/image.jpg`)

## Implementation Details

### Supabase Edge Function

The Edge Function (`supabase/functions/email_subscriptions/index.ts`) handles:

1. **Subscription Requests**:

   - Validates the email format
   - Checks for existing subscribers
   - Adds new subscribers to the database
   - Returns appropriate success/error messages

2. **Unsubscription Requests**:
   - Validates the subscriber ID
   - Removes the subscriber from the database
   - Returns a confirmation message

The function uses CORS headers to allow requests from any origin, making it easy to integrate with your website.

### Email Subscriber Manager

The `EmailSubscriberManager` class (`scripts/posting/email_subscribers.py`) provides an interface to interact with the Supabase database:

- `get_active_subscribers()`: Fetches only active subscribers
- `get_all_subscribers()`: Fetches all subscribers, including inactive ones

It uses the Supabase REST API to communicate with the database.

### Resend Platform

The `ResendPlatform` class (`scripts/posting/platforms/resend.py`) handles:

1. **Email Generation**:

   - Loads the email template
   - Processes content based on the specified content type
   - Replaces placeholders with actual content

2. **Email Sending**:
   - Fetches active subscribers
   - Creates personalized unsubscribe links
   - Sends emails individually to each subscriber
   - Tracks and reports sending results

## Adding a Subscription Form to Your Website

To add a subscription form to your website, include the following HTML:

```html
<form id="subscribe-form">
  <input type="email" id="email" placeholder="Your email address" required />
  <button type="submit">Subscribe</button>
  <div id="subscribe-message"></div>
</form>

<script>
  document
    .getElementById("subscribe-form")
    .addEventListener("submit", async (e) => {
      e.preventDefault();
      const email = document.getElementById("email").value;
      const messageEl = document.getElementById("subscribe-message");

      try {
        const response = await fetch(
          "https://your-project-id.functions.supabase.co/email_subscriptions",
          {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
            },
            body: JSON.stringify({ email }),
          }
        );

        const data = await response.json();

        if (data.success) {
          messageEl.textContent = data.message;
          messageEl.style.color = "green";
          document.getElementById("email").value = "";
        } else {
          messageEl.textContent =
            data.error || "An error occurred. Please try again.";
          messageEl.style.color = "red";
        }
      } catch (error) {
        messageEl.textContent = "An error occurred. Please try again.";
        messageEl.style.color = "red";
      }
    });
</script>
```

Replace `your-project-id` with your actual Supabase project ID.

## Troubleshooting

### Supabase Issues

- **Function Deployment Errors**:

  - Check that you have the latest Supabase CLI
  - Verify your project reference is correct
  - Check for TypeScript errors in the function code

- **Database Connection Issues**:

  - Verify your `SUPABASE_URL` and `SUPABASE_SERVICE_ROLE_KEY` are correct
  - Check that the `email_subscribers` table exists
  - Ensure the service role key has the necessary permissions

- **CORS Errors**:
  - The function includes CORS headers, but if you're still having issues, check your request headers
  - Verify that your frontend is sending the correct Content-Type header

### Resend Issues

- **Email Sending Failures**:

  - Check your Resend API key and sender email
  - Verify that you have active subscribers in your database
  - Check the console output for specific error messages

- **Template Loading Errors**:

  - Ensure the path to `templates/email/blog_post.html` is correct
  - Check that the template contains the expected placeholders

- **Unsubscribe Link Issues**:
  - Verify that `SUPABASE_SUBSCRIBE_FUNCTION_URL` is set correctly
  - Check that the subscriber ID is being properly included in the URL

## Performance Considerations

- Emails are sent individually to each subscriber to enable personalized unsubscribe links
- For large subscriber lists, the sending process may take some time
- The system reports progress during sending, showing successful and failed deliveries
- Consider implementing rate limiting if you have a large number of subscribers to avoid hitting Resend's rate limits
