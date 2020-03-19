def make_utf8_corrections(text):
    return text.replace("\xa0;", b'\xe2\x80\x82'.decode('utf-8')).replace("&#x1F;",
                                                                          b'\xe2\x80\x82'.decode('utf-8')).replace(
        "&#xB;", b'\xe2\x80\x82'.decode('utf-8')).replace("&gt;", b'\xe2\x80\x82'.decode('utf-8')).replace("&lt;",
                                                                                                           b'\xe2\x80\x82'.decode(
                                                                                                               'utf-8')).replace(
        "&#x1E;", b'\xe2\x80\x82'.decode('utf-8')).replace("&#xF;", b'\xe2\x80\x82'.decode('utf-8')).replace("&#x1D;",
                                                                                                             b'\xe2\x80\x82'.decode(
                                                                                                                 'utf-8')).replace(
        "&#x1C;", b'\xe2\x80\x82'.decode('utf-8')).replace("&#x1B;", b'\xe2\x80\x82'.decode('utf-8'))

