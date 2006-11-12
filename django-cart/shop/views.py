# A simple django shopping cart, developed from Maximillian Dornseif's work. See:
# http://groups.google.com/group/django-users/browse_thread/thread/96dd3cc6b74f8a1e

# Additions by Eric Woudenberg (eaw@connact.com)

import re

from django.shortcuts import render_to_response
from django.http import HttpResponse, HttpResponseRedirect
from django import template
from models import Cart

# Google Merchant Account for zzz

# Production
# GoogleMerchantKey='xxx'
# GoogleMerchantID='yyy'

# Sandbox
GoogleMerchantKey='xxx'
GoogleMerchantID='yyy'

def testcookie(request):
    request.session.set_test_cookie()
    return HttpResponseRedirect("../")

def addtocart(request, artnr):
    if not request.session.test_cookie_worked():
        return render_to_response('shop/nocookies.html', \
         {}, context_instance=template.RequestContext(request))
    else:
        request.session.delete_test_cookie()
        cart = request.session.get('cart', None) or Cart()
        cart.add_item(artnr)
        cart.set_return_page(request.META['HTTP_REFERER'])
        request.session['cart'] = cart
        return HttpResponseRedirect("/shop/cart")

def cart(request):
    cart = request.session.get('cart', None) or Cart()
    googleCart, googleSig = doGoogleCheckout(cart)
    return render_to_response('shop/cart.html',
              {'cart': cart,
               'paypalCart': doPaypalCheckout(cart),
               'googleCart': googleCart,
               'googleSig': googleSig,
               'googleMerchantKey': GoogleMerchantKey,
               'googleMerchantID': GoogleMerchantID},
              context_instance=template.RequestContext(request))

# Build a google cart and its sig, in base64, according to:
# http://code.google.com/apis/checkout/developer/index.html

import hmac, sha, base64, xml.sax.saxutils

def doGoogleCheckout(cart):
    T = template.loader.get_template('shop/googlecheckout.xml')
    C = template.Context(
            {'cart': cart,
             'edit_url': 'http://dharmatest:8080/shop/cart/',
             'continue_url': xml.sax.saxutils.escape(cart.returnUrl)})
    cart_cleartext = T.render(C)
    cart_sig = hmac.new(GoogleMerchantKey, cart_cleartext, sha).digest()
    cart_base64 = base64.b64encode(cart_cleartext)
    sig_base64 = base64.b64encode(cart_sig)
    return cart_base64, sig_base64

# Build a Paypal shopping cart form's hidden fields according to:
# https://www.paypal.com/us/cgi-bin/webscr?cmd=p/pdn/howto_checkout

def doPaypalCheckout(cart):
    fields = '''<input type="hidden" name="cmd" value="_cart">
                <input type="hidden" name="upload" value="1">
                <input type="hidden" name="business" value="email@business.com">
                <input type="hidden" name="amount" value="%s">
                <input type="hidden" name="item_name" value="Dharma Talks">
                <input type="image" src="http://www.paypal.com/en_US/i/btn/x-click-but01.gif"
                    name="submit" alt="Make payments with PayPal - it's fast, free and secure!">
    ''' % cart.get_total_price()
    i = 0

    for item in cart.items():
        i += 1
        desc = item.summary_description()
        fields += '<input type="hidden" name="quantity_%d" value="%s">\n' % (i, item.count)
        fields += '<input type="hidden" name="item_name_%d" value="%s">\n' % (i, desc)
        fields += '<input type="hidden" name="item_number_%d" value="%s">\n' % (i, item.sku)
        fields += '<input type="hidden" name="amount_%d" value="%s">\n' % (i, item.unitprice)
    return fields

def emptycart(request):
    cart = request.session.get('cart', None) or Cart()
    cart.empty_cart()
    request.session['cart'] = cart		
    return render_to_response('shop/cart.html',
              {'cart': cart},
              context_instance=template.RequestContext(request))

def updatecart(request):
    cart = request.session.get('cart', None) or Cart()
    for k in request.POST:
        if k.startswith('count_'):
            artnr = k.split('_')[1]
            count = request.POST[k]
            count = re.sub(r'[^0-9]', '', count)
            if count == '':
                count = 0
            try:
                count = int(count)
            except:
                count = 1
            cart.update_item(artnr, count)
            request.session['cart'] = cart
    return HttpResponseRedirect("../")
