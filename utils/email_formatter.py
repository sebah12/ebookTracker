class EmailFormatter:
    """Format email to send as HTML."""

    def format_html(date, title, author, old_price, price, href):
        """
        Make HTML body.

        :param : The date.
        :param title: Title of the item.
        :param author: item's author.
        :param old_price: Previous price.
        :param price: Current price.
        :param href: item's webpage.
        :return: string with HTML formatted body.
        """
        html = f"""\
        <html>
          <head><b>Amazon ebook Tracker Price Alert.</b></head>
          <body>
            <p>On {date} the price for:<br>
              <b>{title}</b><br>
              {author}<br>
              Dropped from <span style='color:grey; font-size:12px;font-weight:bold;'>${old_price}</span> to <span style='color:red; font-size:20px;font-weight:bold;'>${price}</span><br>
              Here is the <a href={href}>link</a>.
            </p>
          </body>
        </html>
        """
        return html

    def format_text(date, title, author, old_price, price, href):
        """
        Make TEXT body.

        :param : The date.
        :param title: Title of the item.
        :param author: item's author.
        :param old_price: Previous price.
        :param price: Current price.
        :param href: item's webpage.
        :return: string with HTML formatted body.
        """
        text = f"""\
        Amazon ebook Tracker Price Alert.
        On {date} the price for: {title}
        Dropped from ${old_price} to ${price}
        Here is the link: href
        """
        return text
