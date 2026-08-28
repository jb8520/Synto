#!/usr/bin/env bash
# Create/delete real Discord "test entitlements" against the DEV bot's
# premium SKU, without touching your real subscription or paying anything.
#
# Test entitlements have no starts_at/ends_at - they stay active until you
# delete them, and deleting one fires a real ENTITLEMENT_DELETE gateway
# event, exactly like a refund would. They can't simulate natural expiry
# via ends_at - use test_premium_scenarios.py for that.
#
# NOTE: DEV_BOT_ID must be the bot's *Application ID*
# (Developer Portal -> General Information -> Application ID). For most
# modern Discord apps this is the same snowflake as the bot user ID, but
# double check it there if you get a 401/404 below.
#
# Usage:
#   ./scripts/premium_test_entitlement.sh create <guild_id>
#   ./scripts/premium_test_entitlement.sh delete <entitlement_id>
#   ./scripts/premium_test_entitlement.sh list

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENV_FILE="$SCRIPT_DIR/../.env"

if [ ! -f "$ENV_FILE" ]; then
    echo "Could not find .env at $ENV_FILE" >&2
    exit 1
fi

set -a
# shellcheck disable=SC1090
source "$ENV_FILE"
set +a

: "${DEV_BOT_ID:?DEV_BOT_ID must be set in .env}"
: "${DEV_BOT_TOKEN:?DEV_BOT_TOKEN must be set in .env}"
: "${DEV_SYNTO_PREMIUM_SKU_ID:?DEV_SYNTO_PREMIUM_SKU_ID must be set in .env}"

API_BASE="https://discord.com/api/v10/applications/${DEV_BOT_ID}/entitlements"
AUTH_HEADER="Authorization: Bot ${DEV_BOT_TOKEN}"

usage() {
    cat >&2 <<EOF
Usage:
  $0 create <guild_id>         Create a test entitlement for a guild (fires ENTITLEMENT_CREATE)
  $0 delete <entitlement_id>   Delete a test entitlement (fires ENTITLEMENT_DELETE)
  $0 list                      List entitlements for the dev premium SKU
EOF
    exit 1
}

[ $# -ge 1 ] || usage

command="$1"

case "$command" in
    create)
        [ $# -eq 2 ] || usage
        guild_id="$2"
        echo "Creating test entitlement for guild $guild_id..." >&2
        curl -sS -X POST "$API_BASE" \
            -H "$AUTH_HEADER" \
            -H "Content-Type: application/json" \
            -d "{\"sku_id\": \"${DEV_SYNTO_PREMIUM_SKU_ID}\", \"owner_id\": \"${guild_id}\", \"owner_type\": 1}"
        echo
        echo "^ Save the \"id\" field above - you'll need it to delete this entitlement later." >&2
        ;;
    delete)
        [ $# -eq 2 ] || usage
        entitlement_id="$2"
        echo "Deleting entitlement $entitlement_id (fires ENTITLEMENT_DELETE)..." >&2
        curl -sS -X DELETE "$API_BASE/$entitlement_id" \
            -H "$AUTH_HEADER" \
            -w "\nHTTP %{http_code}\n"
        ;;
    list)
        curl -sS -G "$API_BASE" \
            -H "$AUTH_HEADER" \
            --data-urlencode "sku_ids=${DEV_SYNTO_PREMIUM_SKU_ID}" \
            --data-urlencode "exclude_ended=false"
        echo
        ;;
    *)
        usage
        ;;
esac