Para = function (elem)
   -- if it has {% .... %} on either side, it's a liquid template to pass through,
   -- not markdown.
   if #elem.content and elem.content[1].text and elem.content[1].text:match('{%%') and elem.content[#elem.content].text:match('%%}')
    then
      return pandoc.RawBlock("markdown", pandoc.utils.stringify(elem.content))
   else
     return elem
   end
  end
