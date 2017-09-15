    <div id="auction-list">
      <div>
        {% for item in items.searchResult.item %}
        <div>
          <h1>
            <a target="_blank" href="{{ item.viewItemURL |e}}">
              {{ item.title|e }}
              <img src="{{ item.pictureURLLarge | replace("http://","https://") if item.pictureURLLarge else item.galleryURL | replace("http://","https://") }}" alt="{{item.title}}"/>
            </a>
          </h1>
          <div class="price_tag">
            <a target="_blank" href="{{ item.viewItemURL |e}}">
              <span>
                {{item.sellingStatus.currentPrice.value}} {{item.sellingStatus.currentPrice._currencyId}}
              </span>
            </a>
          </div>
        </div>
        {% if loop.index % in_rows == 0 and loop.index != loop.length %}
      </div>
      <div>
        {% endif %}
        {% else %}
        <h1> no items found</h1>
        {% endfor %}
      </div>
    </div>
