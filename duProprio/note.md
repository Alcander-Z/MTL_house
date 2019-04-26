# step 1

start crawling from the search result URL. e.g. https://duproprio.com/en/search/list?search=true&is_for_sale=1&with_builders=1&parent=1&pageNumber=1&sort=-published_at (__search_result.html__)

The tasks are:

1. get URL of each listed house on the current page, e.g., https://duproprio.com/en/montreal/le-sud-ouest/condo-for-sale/hab-1102-1740-rue-saint-patrick-850336#description, (__sample_house.html__)


2. get URL of "next" to access the next page, until the last one has been viewed.


# step 2

crawl information about the house for sale (or rent).

- ownership
- property style
- price
- floor
- area
- municipal assessment
- year of construction
- backyard faces
- rooms (no. bedroom/bathroom/, etc.)
- address
- id
- other information worth paying attention
