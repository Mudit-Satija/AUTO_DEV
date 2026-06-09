# Blog — Product Pattern

## Common Pages
- **Blog Home** — list of posts (featured, recent, paginated)
- **Post Detail** — full article with author, date, tags, comments
- **Category Page** — posts filtered by category
- **Tag Page** — posts filtered by tag
- **Author Page** — posts by specific author with bio
- **Search Results** — posts matching search query
- **Admin Posts** — CRUD for blog posts with editor
- **Admin Categories/Tags** — taxonomy management
- **Admin Comments** — moderation queue

## Common Entities
- Post (title, slug, content, excerpt, featured_image, status, published_at)
- Author (name, bio, avatar, social links)
- Category (name, slug, description)
- Tag (name, slug)
- Comment (author, email, content, status, post_id, parent_id)
- Media (file, alt_text, caption, post_id)
- NewsletterSubscriber (email, subscribed_at, status)

## Common Workflows
1. Reader lands on blog home → sees featured post + recent list
2. Reader clicks post → reads full article with related posts
3. Reader leaves comment → moderated → published
4. Reader subscribes to newsletter → confirmation email sent
5. Admin creates post → writes in editor → sets category/tags → publishes
6. Admin moderates comments → approve/reject

## Common API Endpoints
| Method | Path | Action |
|--------|------|--------|
| GET | /api/posts | Published posts (paginated, filterable) |
| GET | /api/posts/:slug | Single post by slug |
| GET | /api/categories | Category list with post counts |
| GET | /api/tags | Tag list with post counts |
| GET | /api/posts/search?q= | Search posts |
| POST | /api/comments | Submit comment |
| GET | /api/comments/:postId | Comments for a post |
| POST | /api/newsletter/subscribe | Email subscribe |
| POST | /api/admin/posts | Create/edit post |
| PUT | /api/admin/comments/:id | Moderate comment |

## Common UI Components
- **Post Card** — featured image, title, excerpt, date, author avatar
- **Post Grid/List** — responsive layout (grid for featured, list for recent)
- **Category/Tag Badge** — clickable pill/tag
- **Author Bio Card** — avatar, name, short bio, social links
- **Comment Thread** — nested replies with form
- **Rich Text Editor** — content editing with image upload
- **Share Buttons** — social media sharing
- **Newsletter Form** — email input + subscribe button
- **Search Bar** — text input with live suggestions

## Common Dashboards
- **Content Dashboard**: posts published (line), views (area), comments (bar), top posts (table)
- **Engagement Dashboard**: time on page, bounce rate, social shares, subscriber growth

## Common Reports
- Most popular posts (by views, comments, shares)
- Traffic sources and referral breakdown
- Newsletter growth and open rates
- Content calendar (published vs scheduled)
