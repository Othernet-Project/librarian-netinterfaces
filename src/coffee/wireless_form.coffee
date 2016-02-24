((window, $) ->
  NORTH_AMERICA = ['US', 'CA']

  form = $ '#wireless-form'
  url = form.attr 'action'

  generateOptions = (range) ->
    options = []
    for n in [1..range]
      options.push "<option value=\"#{n}\">#{n}</option>\n"
    return options.join()


  updateChannels = () ->
    countryField = $ '#country'
    channelField = $ '#channel'
    country = countryField.val()
    current = channelField.val()
    range = if country in NORTH_AMERICA then 11 else 13
    if current > range
      current = range
    options = generateOptions range
    (channelField.html options).val current


  togglePassword = () ->
    securityField = $ '#security'
    passwordField = $ '#password'
    passwordWrapper = passwordField.parents 'p.o-field'
    hasSecurity = securityField.val() isnt '0'
    passwordWrapper.toggle hasSecurity


  submitForm = (e) ->
    e.preventDefault()
    res = $.post url, form.serialize()
    res.done (data) ->
      form.html data
      ($ window).trigger 'wireless-updated'
      (form.parents '.o-collapsible-section').trigger 'remax'
      togglePassword()
      updateChannels()
    res.fail () ->
      form.prepend errorMessage


  form.on 'change', '#security', togglePassword
  form.on 'change', '#country', updateChannels
  form.on 'submit', submitForm

  togglePassword()
  updateChannels()
)(this, this.jQuery)
