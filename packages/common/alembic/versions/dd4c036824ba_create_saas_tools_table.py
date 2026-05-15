"""create_saas_tools_table

Revision ID: dd4c036824ba
Revises: ed4f2bc84da8
Create Date: 2026-05-14 18:29:20.124782

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'dd4c036824ba'
down_revision: Union[str, Sequence[str], None] = 'ed4f2bc84da8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

TOOLS = [
    # cloud
    {"name": "AWS", "category": "cloud", "website_url": "https://aws.amazon.com"},
    {"name": "Google Cloud Platform", "category": "cloud", "website_url": "https://cloud.google.com"},
    {"name": "Microsoft Azure", "category": "cloud", "website_url": "https://azure.microsoft.com"},
    {"name": "Vercel", "category": "cloud", "website_url": "https://vercel.com"},
    {"name": "Netlify", "category": "cloud", "website_url": "https://netlify.com"},
    {"name": "Railway", "category": "cloud", "website_url": "https://railway.app"},
    {"name": "Render", "category": "cloud", "website_url": "https://render.com"},
    {"name": "DigitalOcean", "category": "cloud", "website_url": "https://digitalocean.com"},
    {"name": "Hetzner Cloud", "category": "cloud", "website_url": "https://hetzner.com"},
    {"name": "Cloudflare", "category": "cloud", "website_url": "https://cloudflare.com"},
    {"name": "OVHcloud", "category": "cloud", "website_url": "https://ovhcloud.com"},
    {"name": "Heroku", "category": "cloud", "website_url": "https://heroku.com"},
    # payments
    {"name": "Stripe", "category": "payments", "website_url": "https://stripe.com"},
    {"name": "PayPal", "category": "payments", "website_url": "https://paypal.com"},
    {"name": "Adyen", "category": "payments", "website_url": "https://adyen.com"},
    {"name": "Mollie", "category": "payments", "website_url": "https://mollie.com"},
    {"name": "Paddle", "category": "payments", "website_url": "https://paddle.com"},
    {"name": "GoCardless", "category": "payments", "website_url": "https://gocardless.com"},
    {"name": "Braintree", "category": "payments", "website_url": "https://braintreepayments.com"},
    {"name": "Chargebee", "category": "payments", "website_url": "https://chargebee.com"},
    # crm
    {"name": "Salesforce", "category": "crm", "website_url": "https://salesforce.com"},
    {"name": "HubSpot", "category": "crm", "website_url": "https://hubspot.com"},
    {"name": "Pipedrive", "category": "crm", "website_url": "https://pipedrive.com"},
    {"name": "Freshsales", "category": "crm", "website_url": "https://freshworks.com/crm"},
    {"name": "Zoho CRM", "category": "crm", "website_url": "https://zoho.com/crm"},
    {"name": "Copper", "category": "crm", "website_url": "https://copper.com"},
    {"name": "Close", "category": "crm", "website_url": "https://close.com"},
    # support
    {"name": "Intercom", "category": "support", "website_url": "https://intercom.com"},
    {"name": "Zendesk", "category": "support", "website_url": "https://zendesk.com"},
    {"name": "Freshdesk", "category": "support", "website_url": "https://freshdesk.com"},
    {"name": "Crisp", "category": "support", "website_url": "https://crisp.chat"},
    {"name": "Help Scout", "category": "support", "website_url": "https://helpscout.com"},
    {"name": "Tidio", "category": "support", "website_url": "https://tidio.com"},
    {"name": "Drift", "category": "support", "website_url": "https://drift.com"},
    # analytics
    {"name": "Google Analytics", "category": "analytics", "website_url": "https://analytics.google.com"},
    {"name": "Mixpanel", "category": "analytics", "website_url": "https://mixpanel.com"},
    {"name": "Amplitude", "category": "analytics", "website_url": "https://amplitude.com"},
    {"name": "PostHog", "category": "analytics", "website_url": "https://posthog.com"},
    {"name": "Plausible Analytics", "category": "analytics", "website_url": "https://plausible.io"},
    {"name": "Segment", "category": "analytics", "website_url": "https://segment.com"},
    {"name": "Matomo", "category": "analytics", "website_url": "https://matomo.org"},
    {"name": "Hotjar", "category": "analytics", "website_url": "https://hotjar.com"},
    # email
    {"name": "Mailchimp", "category": "email", "website_url": "https://mailchimp.com"},
    {"name": "SendGrid", "category": "email", "website_url": "https://sendgrid.com"},
    {"name": "Postmark", "category": "email", "website_url": "https://postmarkapp.com"},
    {"name": "Brevo", "category": "email", "website_url": "https://brevo.com"},
    {"name": "Resend", "category": "email", "website_url": "https://resend.com"},
    {"name": "Klaviyo", "category": "email", "website_url": "https://klaviyo.com"},
    {"name": "ActiveCampaign", "category": "email", "website_url": "https://activecampaign.com"},
    {"name": "Customer.io", "category": "email", "website_url": "https://customer.io"},
    # auth
    {"name": "Clerk", "category": "auth", "website_url": "https://clerk.com"},
    {"name": "Auth0", "category": "auth", "website_url": "https://auth0.com"},
    {"name": "Okta", "category": "auth", "website_url": "https://okta.com"},
    {"name": "Firebase Authentication", "category": "auth", "website_url": "https://firebase.google.com"},
    {"name": "OneLogin", "category": "auth", "website_url": "https://onelogin.com"},
    # storage
    {"name": "Amazon S3", "category": "storage", "website_url": "https://aws.amazon.com/s3"},
    {"name": "Cloudflare R2", "category": "storage", "website_url": "https://cloudflare.com/r2"},
    {"name": "Supabase", "category": "storage", "website_url": "https://supabase.com"},
    {"name": "MongoDB Atlas", "category": "storage", "website_url": "https://mongodb.com/atlas"},
    {"name": "Snowflake", "category": "storage", "website_url": "https://snowflake.com"},
    # monitoring
    {"name": "Sentry", "category": "monitoring", "website_url": "https://sentry.io"},
    {"name": "Datadog", "category": "monitoring", "website_url": "https://datadoghq.com"},
    {"name": "New Relic", "category": "monitoring", "website_url": "https://newrelic.com"},
    {"name": "Grafana Cloud", "category": "monitoring", "website_url": "https://grafana.com"},
    {"name": "Dynatrace", "category": "monitoring", "website_url": "https://dynatrace.com"},
    {"name": "LogRocket", "category": "monitoring", "website_url": "https://logrocket.com"},
    # communication
    {"name": "Slack", "category": "communication", "website_url": "https://slack.com"},
    {"name": "Microsoft Teams", "category": "communication", "website_url": "https://microsoft.com/teams"},
    {"name": "Twilio", "category": "communication", "website_url": "https://twilio.com"},
    {"name": "Zoom", "category": "communication", "website_url": "https://zoom.us"},
    {"name": "Google Workspace", "category": "communication", "website_url": "https://workspace.google.com"},
    {"name": "Microsoft 365", "category": "communication", "website_url": "https://microsoft.com/365"},
    {"name": "Notion", "category": "communication", "website_url": "https://notion.so"},
    {"name": "Loom", "category": "communication", "website_url": "https://loom.com"},
    # hr
    {"name": "Workday", "category": "hr", "website_url": "https://workday.com"},
    {"name": "BambooHR", "category": "hr", "website_url": "https://bamboohr.com"},
    {"name": "Personio", "category": "hr", "website_url": "https://personio.com"},
    {"name": "HiBob", "category": "hr", "website_url": "https://hibob.com"},
    {"name": "Rippling", "category": "hr", "website_url": "https://rippling.com"},
    {"name": "Factorial", "category": "hr", "website_url": "https://factorialhr.com"},
    # finance
    {"name": "QuickBooks", "category": "finance", "website_url": "https://quickbooks.intuit.com"},
    {"name": "Xero", "category": "finance", "website_url": "https://xero.com"},
    {"name": "Recurly", "category": "finance", "website_url": "https://recurly.com"},
    {"name": "Pleo", "category": "finance", "website_url": "https://pleo.io"},
    {"name": "Pennylane", "category": "finance", "website_url": "https://pennylane.com"},
    # sales
    {"name": "LinkedIn Sales Navigator", "category": "sales", "website_url": "https://linkedin.com/sales"},
    {"name": "Apollo.io", "category": "sales", "website_url": "https://apollo.io"},
    {"name": "Outreach", "category": "sales", "website_url": "https://outreach.io"},
    {"name": "Salesloft", "category": "sales", "website_url": "https://salesloft.com"},
    {"name": "Lemlist", "category": "sales", "website_url": "https://lemlist.com"},
    # devtools
    {"name": "Jira", "category": "devtools", "website_url": "https://atlassian.com/jira"},
    {"name": "Linear", "category": "devtools", "website_url": "https://linear.app"},
    {"name": "Asana", "category": "devtools", "website_url": "https://asana.com"},
    {"name": "GitHub", "category": "devtools", "website_url": "https://github.com"},
    {"name": "GitLab", "category": "devtools", "website_url": "https://gitlab.com"},
    {"name": "Figma", "category": "devtools", "website_url": "https://figma.com"},
    {"name": "Miro", "category": "devtools", "website_url": "https://miro.com"},
    # video
    {"name": "Vimeo", "category": "video", "website_url": "https://vimeo.com"},
    {"name": "Wistia", "category": "video", "website_url": "https://wistia.com"},
    {"name": "Livestorm", "category": "video", "website_url": "https://livestorm.co"},
    # legal
    {"name": "DocuSign", "category": "legal", "website_url": "https://docusign.com"},
    {"name": "HelloSign", "category": "legal", "website_url": "https://hellosign.com"},
    {"name": "PandaDoc", "category": "legal", "website_url": "https://pandadoc.com"},
    {"name": "Adobe Sign", "category": "legal", "website_url": "https://acrobat.adobe.com/sign"},
    {"name": "Contractbook", "category": "legal", "website_url": "https://contractbook.com"},
    # recruitment
    {"name": "Greenhouse", "category": "recruitment", "website_url": "https://greenhouse.io"},
    {"name": "Lever", "category": "recruitment", "website_url": "https://lever.co"},
    {"name": "Workable", "category": "recruitment", "website_url": "https://workable.com"},
    {"name": "Ashby", "category": "recruitment", "website_url": "https://ashbyhq.com"},
    {"name": "Teamtailor", "category": "recruitment", "website_url": "https://teamtailor.com"},
    {"name": "Recruitee", "category": "recruitment", "website_url": "https://recruitee.com"},
    # eor
    {"name": "Deel", "category": "eor", "website_url": "https://deel.com"},
    {"name": "Remote", "category": "eor", "website_url": "https://remote.com"},
    {"name": "Oyster HR", "category": "eor", "website_url": "https://oysterhr.com"},
    {"name": "Workmotion", "category": "eor", "website_url": "https://workmotion.com"},
    {"name": "Lano", "category": "eor", "website_url": "https://lano.io"},
    # feature-flags
    {"name": "LaunchDarkly", "category": "feature-flags", "website_url": "https://launchdarkly.com"},
    {"name": "Flagsmith", "category": "feature-flags", "website_url": "https://flagsmith.com"},
    {"name": "Split.io", "category": "feature-flags", "website_url": "https://split.io"},
    {"name": "Unleash", "category": "feature-flags", "website_url": "https://getunleash.io"},
    # devops
    {"name": "CircleCI", "category": "devops", "website_url": "https://circleci.com"},
    {"name": "Buildkite", "category": "devops", "website_url": "https://buildkite.com"},
    {"name": "Terraform Cloud", "category": "devops", "website_url": "https://terraform.io"},
    {"name": "Pulumi", "category": "devops", "website_url": "https://pulumi.com"},
    {"name": "Docker Hub", "category": "devops", "website_url": "https://hub.docker.com"},
    # security
    {"name": "1Password", "category": "security", "website_url": "https://1password.com"},
    {"name": "Vanta", "category": "security", "website_url": "https://vanta.com"},
    {"name": "Drata", "category": "security", "website_url": "https://drata.com"},
    {"name": "Wiz", "category": "security", "website_url": "https://wiz.io"},
    {"name": "Snyk", "category": "security", "website_url": "https://snyk.io"},
    # customer-success
    {"name": "Gainsight", "category": "customer-success", "website_url": "https://gainsight.com"},
    {"name": "ChurnZero", "category": "customer-success", "website_url": "https://churnzero.com"},
    {"name": "Vitally", "category": "customer-success", "website_url": "https://vitally.io"},
    {"name": "Planhat", "category": "customer-success", "website_url": "https://planhat.com"},
    # seo
    {"name": "Semrush", "category": "seo", "website_url": "https://semrush.com"},
    {"name": "Ahrefs", "category": "seo", "website_url": "https://ahrefs.com"},
    {"name": "Contentful", "category": "seo", "website_url": "https://contentful.com"},
    {"name": "Sanity", "category": "seo", "website_url": "https://sanity.io"},
    # social-ads
    {"name": "Hootsuite", "category": "social-ads", "website_url": "https://hootsuite.com"},
    {"name": "Buffer", "category": "social-ads", "website_url": "https://buffer.com"},
    {"name": "Meta Business Suite", "category": "social-ads", "website_url": "https://business.facebook.com"},
    {"name": "Google Ads", "category": "social-ads", "website_url": "https://ads.google.com"},
    # cms
    {"name": "Webflow", "category": "cms", "website_url": "https://webflow.com"},
    {"name": "Storyblok", "category": "cms", "website_url": "https://storyblok.com"},
    {"name": "Ghost", "category": "cms", "website_url": "https://ghost.org"},
    {"name": "Prismic", "category": "cms", "website_url": "https://prismic.io"},
    # data-enrichment
    {"name": "Clearbit", "category": "data-enrichment", "website_url": "https://clearbit.com"},
    {"name": "ZoomInfo", "category": "data-enrichment", "website_url": "https://zoominfo.com"},
    {"name": "Lusha", "category": "data-enrichment", "website_url": "https://lusha.com"},
    {"name": "Hunter.io", "category": "data-enrichment", "website_url": "https://hunter.io"},
    # feedback
    {"name": "Typeform", "category": "feedback", "website_url": "https://typeform.com"},
    {"name": "SurveyMonkey", "category": "feedback", "website_url": "https://surveymonkey.com"},
    {"name": "Delighted", "category": "feedback", "website_url": "https://delighted.com"},
    {"name": "Canny", "category": "feedback", "website_url": "https://canny.io"},
    # automation
    {"name": "Retool", "category": "automation", "website_url": "https://retool.com"},
    {"name": "Airtable", "category": "automation", "website_url": "https://airtable.com"},
    {"name": "Zapier", "category": "automation", "website_url": "https://zapier.com"},
    {"name": "Make", "category": "automation", "website_url": "https://make.com"},
    {"name": "n8n", "category": "automation", "website_url": "https://n8n.io"},
    # expense
    {"name": "Spendesk", "category": "expense", "website_url": "https://spendesk.com"},
    {"name": "Expensify", "category": "expense", "website_url": "https://expensify.com"},
    {"name": "Brex", "category": "expense", "website_url": "https://brex.com"},
    {"name": "Ramp", "category": "expense", "website_url": "https://ramp.com"},
    {"name": "Moss", "category": "expense", "website_url": "https://getmoss.com"},
    # bi
    {"name": "Tableau", "category": "bi", "website_url": "https://tableau.com"},
    {"name": "Looker", "category": "bi", "website_url": "https://looker.com"},
    {"name": "Metabase", "category": "bi", "website_url": "https://metabase.com"},
    {"name": "dbt Cloud", "category": "bi", "website_url": "https://getdbt.com"},
    {"name": "Airbyte", "category": "bi", "website_url": "https://airbyte.com"},
    # video (extended)
    {"name": "Mux", "category": "video", "website_url": "https://mux.com"},
    {"name": "Daily.co", "category": "video", "website_url": "https://daily.co"},
    {"name": "Whereby", "category": "video", "website_url": "https://whereby.com"},
    {"name": "Descript", "category": "video", "website_url": "https://descript.com"},
    # productivity
    {"name": "Confluence", "category": "productivity", "website_url": "https://atlassian.com/confluence"},
    {"name": "Coda", "category": "productivity", "website_url": "https://coda.io"},
    {"name": "Slite", "category": "productivity", "website_url": "https://slite.com"},
    {"name": "Basecamp", "category": "productivity", "website_url": "https://basecamp.com"},
    {"name": "Trello", "category": "productivity", "website_url": "https://trello.com"},
    # localization
    {"name": "Lokalise", "category": "localization", "website_url": "https://lokalise.com"},
    {"name": "Phrase", "category": "localization", "website_url": "https://phrase.com"},
    {"name": "Crowdin", "category": "localization", "website_url": "https://crowdin.com"},
    # scheduling
    {"name": "Calendly", "category": "scheduling", "website_url": "https://calendly.com"},
    {"name": "SavvyCal", "category": "scheduling", "website_url": "https://savvycal.com"},
    {"name": "Cal.com", "category": "scheduling", "website_url": "https://cal.com"},
    # search
    {"name": "Algolia", "category": "search", "website_url": "https://algolia.com"},
    {"name": "Elastic Cloud", "category": "search", "website_url": "https://elastic.co"},
    # ai-api
    {"name": "OpenAI API", "category": "ai-api", "website_url": "https://openai.com"},
    {"name": "Anthropic API", "category": "ai-api", "website_url": "https://anthropic.com"},
    {"name": "Cohere", "category": "ai-api", "website_url": "https://cohere.com"},
    # shared-inbox
    {"name": "Front", "category": "shared-inbox", "website_url": "https://front.com"},
    {"name": "Superhuman", "category": "shared-inbox", "website_url": "https://superhuman.com"},
    {"name": "Missive", "category": "shared-inbox", "website_url": "https://missiveapp.com"},
    # billing
    {"name": "Zuora", "category": "billing", "website_url": "https://zuora.com"},
    {"name": "FastSpring", "category": "billing", "website_url": "https://fastspring.com"},
    {"name": "Maxio", "category": "billing", "website_url": "https://maxio.com"},
    # cdn
    {"name": "Fastly", "category": "cdn", "website_url": "https://fastly.com"},
    {"name": "Akamai", "category": "cdn", "website_url": "https://akamai.com"},
    {"name": "BunnyCDN", "category": "cdn", "website_url": "https://bunny.net"},
    # knowledge-base
    {"name": "Guru", "category": "knowledge-base", "website_url": "https://getguru.com"},
    {"name": "Document360", "category": "knowledge-base", "website_url": "https://document360.com"},
]


def upgrade() -> None:
    saas_tools = op.create_table(
        "saas_tools",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("tool_id", sa.String(32), nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("category", sa.String(50), nullable=False, server_default="other"),
        sa.Column("website_url", sa.String(255), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("tool_id"),
        sa.UniqueConstraint("name"),
    )

    from nanoid import generate
    op.bulk_insert(
        saas_tools,
        [
            {
                "tool_id": f"tol_{generate(size=8)}",
                "name": t["name"],
                "category": t["category"],
                "website_url": t["website_url"],
                "is_active": True,
            }
            for t in TOOLS
        ],
    )


def downgrade() -> None:
    op.drop_table("saas_tools")