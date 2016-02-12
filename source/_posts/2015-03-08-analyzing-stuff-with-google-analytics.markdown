---
layout: post
title: "Analyzing Stuff With Google Analytics"
date: 2015-03-08 12:37:36 +0530
comments: true
categories: [nereid, google]
---

This article offers a glimpse into how we implemented Google Analytics procedures,
such as click tracking, in our generic webstore - [Nereid Webshop](https://github.com/openlabs/nereid-webshop).

<!--more-->

As a beginner in Javascript, I was tasked with tracking clicks from various areas
of the webstore, such as product pages, the search page, etc. Google's developer
documentation ([here](https://developers.google.com/analytics/)) is a good place
to start. Note that we used the more recent ga.js, as opposed to the older
analytics.js script.

First we wrote our backend implementation - to fetch the details of a product.
The basic Product model is in the core [Product](https://github.com/tryton/product) repository.
We added a few attributes of our own in our own repos.

``` python ga data method
def ga_product_data(self, **kwargs):
    '''
    Return a dictionary of the product information as expected by Google
    Analytics
    Other possible values for kwargs include -:
    :param list: The name of the list in which this impression is to be
                 recorded
    :param position: Integer position of the item on the view
    '''
    rv = {
        'id': self.code or unicode(self.id),
        'name': self.name,
        'category': self.category and self.category.name or None,
    }
    rv.update(kwargs)
    return rv
```

Once we had that in place, we began by analyzing what parts of our webstore needed
analytics. A typical product page contains various link-points where we could
insert our GA attributes. Some of these could be -:

* Add to cart button
* Related product links
* Add related products to cart button

For example, in our form for adding the product to cart -:

{% raw %}
``` html add to cart
<form action="{{ url_for("nereid.cart.add_to_cart") }}" method="post" id="product-buy-now" class="add-to-cart" autocomplete="off" data-ga-event-label="Add To Cart" data-ga-product-name="{{ product.name }}" data-ga-product-category="{{ product.category and product.category.name or None }}" data-ga-product-price="{{ product.sale_price()|currencyformat(request.nereid_currency.code) }}">
  <input type="hidden" name="csrf_token" value="{{ csrf_token() }}" />
  <input type="hidden" name="quantity" value="1"/>
  <input type="hidden" name="size" id="size-id"/>
  <input type="hidden" name="product" value="{{ product.id }}"/>
  <input type="hidden" name="action" value="add"/>
  <button class="btn btn-primary btn-buynow btn-block btn-lg" type="submit" {% if not product.can_buy_from_eshop() %}disabled{% endif %}
    quantity="1" id="buy-now-btn">Buy Now</button>
</form>
```
{% endraw %}

Similarly, we could have the following on a product link -:

{% raw %}
``` html product link
<a href="{{ related_product.get_absolute_url() }}" ga-product-link data-ga-product-list="Related Products" data-ga-event-label="Product Thumbnail" data-ga-product-id="{{ related_product.id }}" data-ga-product-name="{{ related_product.name }}" data-ga-product-category="{{ related_product.category and related_product.category.name or None }}">
  <img src="{{ CDN }}{{ related_product.default_image.transform_command().thumbnail(200, 200, 'a') }}" class="img margin-auto" alt="{{ related_product.name }}">
</a>
```
{% endraw %}

Note the `data-ga` prefixed attributes in the `form` tag. These are used in
conjunction with jQuery's data() method to fetch product attributes, to be sent
to Google's servers.

The JS snippet for tracking product clicks is as follows (assuming GA is set up already) -:

``` javascript product click
$(function (){
  $('a[href][ga-product-link]').on("click", function(e){
    if(typeof ga == 'undefined'){
      return true;
    }
    e.preventDefault();
    e.stopPropagation();
    var url = $(this).attr('href');
    // register safety net timeout:
    var t = setTimeout(function() {
      document.location.href = url
    }, 500);
    ga('ec:addProduct', {
      'id': $(this).data('ga-product-id'),
      'name': $(this).data('ga-product-name'),
      'category': $(this).data('ga-product-category')
    });
    ga('ec:setAction', 'click', {list: $(this).data('ga-product-list')});
    ga('send', 'event', 'Product', 'click', $(this).data('ga-event-label') || '', {
      'hitCallback': function() {
        clearTimeout(t);
        // redirect anyway:
        document.location.href = url;
      }});
  });
});
```

I'll break this down step by step -:

* First, we collect all those anchor tags on the page which have the `ga-product-link` attribute.
  We register our method on the click event.
* We need `preventDefault()` and `stopPropagation()` to temporarily disable default behaviour,
  i.e., taking us to a different page.
* We register a **safety net timeout**. This step is crucial - we don't want our page
  loading to take forever or never happen just because the data wasn't sent to the
  GA servers successfully.
* We perform a `addProduct` call with product details and then use `setAction`
  to denote that this was a product click - and send data describing the event -
  which in this case was a click on a related product.
* We also register a callback which clears our earlier timeout and redirects to
  the desired location. This is in the normal case - that the data was sent successfully.
  If the data isn't sent, the redirect is done on timeout completion.

Tracking product additions to cart was slightly trickier. We need to take care of
form submission in the add to cart case.

``` javascript add to cart
$(function() {
  $('.add-to-cart').submit(function(e){
    if(typeof ga == 'undefined'){
      return true;
    }
    e.preventDefault();
    var alreadySubmitted = false;
    var form = this;
    /* The code below registers a timeout which acts
     * as a safety net. The boolean alreadySubmitted is used
     * to check whether the form was already submitted or not.
     * It is used by the callbacks in setTimeout and GA. It is to
     * avoid the specific cases where both callbacks fire, resulting
     * in a double form submission.
     */
    var t = setTimeout(function() {
      if (alreadySubmitted) return;
      alreadySubmitted = true;
      form.submit();
    }, 500);
    ga('ec:addProduct', {
      'id': $(this).children("input[name='product']").attr('value'),
      'name': $(this).data('ga-product-name'),
      'category': $(this).data('ga-product-category'),
      'price': $(this).data('ga-product-price'),
      'quantity': $(this).children("input[name='quantity']").attr('value'),
    });
    ga('ec:setAction', 'add');
    ga('send', 'event', 'CartAnalytics', 'click', $(this).data('ga-event-label') || '', {
      'hitCallback': function() {
        if (alreadySubmitted) return;
        alreadySubmitted = true;
        // Submit anyway
        form.submit();
      }});
  });
});
```

In this case, nearly everything is the same, except the use of a boolean - `alreadySubmitted`.
This boolean is checked in both cases - when the data is sent succesfully to the GA servers,
and when it is not and form submission should not be delayed, and *also* to prevent
a double form submission - an edge case which I was able to consistently reproduce.

We also implemented product removal from cart in a similar manner. You can peruse
the webshop source at your leisure - it is open-source, and we encourage good pull requests.

My next article will be on one of my favourite tools - Elasticsearch :-).
