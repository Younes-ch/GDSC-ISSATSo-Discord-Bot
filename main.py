import discord
from discord.ext import commands
import os
import requests
import json
from keep_alive import keep_alive
import logging
import asyncio

intents = discord.Intents(messages=True, guilds=True, members=True, dm_reactions=True, reactions=True)
logging.basicConfig(level=logging.INFO)
bot = commands.Bot(command_prefix='&', intents=intents)
bot.remove_command('help')
cmds = [
  {
    'name' : 'avatar',  
    'args' : '[**member**]',
    'dis' : 'Returns the avatar of the member mentioned or the user who called the command (in case no one was mentioned).'
  },
  {
    'name' : 'meme',  
    'args' : '[**subreddit name**]',
    'dis' : 'Returns a random picture from the subbredit you provide or Dankmemes/memes/me_irl (in case no Subbredit name was provided).'
  },
  { 
    'name' : 'weather',  
    'args' : '[**city name**]',
    'dis' : 'Returns current weather in the city mentioned.'
  },
  {
    'name' : 'say',
    'args' : '[**message**]',
    'dis' : 'Sends the message as the bot.'
  },
  {
    "name" : 'fact', 
    'args' : '',
    'dis' : 'Returns a random fact.'
  },
  {
    "name" : 'corona', 
    'args' : '[**country name**]',
    'dis' : 'Returns today''s COVID-19 statistics of the mentioned country (Tunisia if none was mentioned).'
  },
  {
    "name" : 'snipe',  
    'args' : '',
    'dis' : 'Returns last deleted messages in the channel where the command was called.'
  },
  {
    "name" : 'rps', 
    'args' : '[**member**]',
    'dis' : 'Creates a RPS game between you and the mentioned member.'
  },
  {
    "name" : 'joke', 
    'args' : '[**word**]',
    'dis' : 'Returns a random joke contains the word (word argument can be omitted).'
  },
  {
    "name" : 'movie', 
    'args' : '[**movie name**]',
    'dis' : 'Returns detailed information about the movie mentioned.'
  },
  {
    "name" : 'ping', 
    'args' : '',
    'dis' : 'Returns your current client ping.'
  },
  {
    "name" : 'quote', 
    'args' : '',
    'dis' : 'Returns a random quote.'
  },
  {
    "name" : 'help', 
    'args' : '',
    'dis' : 'Shows this message.'
  }
]

def get_random_quote():
  response = requests.get('https://zenquotes.io/api/random')
  json_data = json.loads(response.text)
  random_quote = f'{json_data[0]["q"]}|{json_data[0]["a"]}'
  return random_quote


def get_random_fact():
  response = requests.get('https://uselessfacts.jsph.pl/random.json?language=en')
  json_data = json.loads(response.text)
  useless_fact = f'{json_data["text"]}'
  return useless_fact



#help command
@bot.group(invoke_without_command=True)
async def help(ctx):
  embed = discord.Embed(title='Commands:', color=0x70e68a)
  embed.set_footer(text='Requested by {}'.format(ctx.author), icon_url = ctx.author.avatar_url)
  embed.set_author(name='Github Link', icon_url='https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png')
  global cmds
  for cmd in cmds:
    embed.add_field(name=f'{cmd["name"].capitalize()}:', value=f'`&{cmd["name"]} {cmd["args"]}` : {cmd["dis"]}', inline=False)
    
  await ctx.send(embed=embed)

#weather command
@bot.command()
async def weather(ctx, *, city : str = None):
  url = 'https://api.openweathermap.org/data/2.5/weather?q={}&appid={}'.format("%20".join(city.split()), os.getenv('WEATHER')) if city else 'https://api.openweathermap.org/data/2.5/weather?q=Sousse&appid={}'.format(os.getenv('WEATHER'))

  response = requests.get(url)
  json_data = json.loads(response.text)
  
  if 'message' in json_data.keys():
    await ctx.message.add_reaction('❌')
    await ctx.reply(json_data['message'].capitalize() + '.', mention_author=False)
  else:
    country_code = json_data['sys']['country'].lower()
    city = json_data['name']
    weather_main = json_data['weather'][0]['main']
    weather_description = json_data['weather'][0]['description']
    weather_icon = 'https://openweathermap.org/img/wn/' + json_data['weather'][0]['icon'] + '@2x.png'
    temperature = str(round(json_data['main']['temp'] - 273.15, 2))
    feels_like = str(round(json_data['main']['feels_like'] - 273.15, 2))
    humidity = str(json_data['main']['humidity']) + '%'
    wind_speed = str(json_data['wind']['speed']) + 'm/s'

    embed = discord.Embed(title=f'Current weather in {city} :flag_{country_code}:', color=ctx.author.top_role.color)
    embed.add_field(name='Weather:', value=weather_main)
    embed.add_field(name='Description:', value=weather_description)
    embed.add_field(name='Temperature:', value=temperature)
    embed.add_field(name='Feels like:', value=feels_like)
    embed.add_field(name='Humidity:', value=humidity)
    embed.add_field(name='Wind speed:', value=wind_speed)
    embed.set_thumbnail(url=weather_icon)
    embed.set_footer(text=f'Requested by {ctx.author}', icon_url=ctx.author.avatar_url)
    await ctx.reply(embed=embed, mention_author=False)

#meme command
@bot.command()
async def meme(ctx, *, subreddit : str = None):
  url = ' https://meme-api.herokuapp.com/gimme' if not subreddit else ' https://meme-api.herokuapp.com/gimme/{}'.format("".join(subreddit.lower()))

  response = requests.get(url)

  json_data = json.loads(response.text)
  if 'subreddit' in json_data.keys():
    subreddit = '/r/' + json_data['subreddit']
    if json_data['nsfw'] == True:
      await ctx.reply('The meme you requested contains nsfw content.', delete_after=5, mention_author=False)
      await asyncio.sleep(5)
      await ctx.message.delete()
    else:
      await ctx.reply('Here is a meme from {}'.format(subreddit), mention_author=False)
      await ctx.send(json_data['url'])
  else:
    await ctx.message.add_reaction('❌')
    await ctx.reply(json_data['message'], mention_author=False)

#fact command
@bot.command()
async def fact(ctx):
  embed = discord.Embed(title='Random Fact:', description=get_random_fact(), color=ctx.author.top_role.color)
  embed.set_thumbnail(url='https://image.shutterstock.com/image-illustration/fun-facts-colorful-stripes-260nw-683840437.jpg')
  embed.set_footer(text=f'Requested by {ctx.author}', icon_url=ctx.author.avatar_url)
  await ctx.reply(embed=embed, mention_author=False)

@bot.event
async def on_ready():
  print('------')
  print('Logged in as')
  print(bot.user.name)
  print(bot.user.id)
  print('------')

#rps command
@bot.command()
async def rps(ctx, *, member : discord.Member):
  if ctx.author == member or member.bot:
    raise commands.MemberNotFound
  else:
    message = await ctx.send('`Creating a RPS game...`', mention_author=False)
    embed = discord.Embed(title='Rock Paper Scissors:', description='**Who will win? 🤔**', color=ctx.author.top_role.color)
    embed.set_thumbnail(url='https://facts.net/wp-content/uploads/2020/11/rock-paper-scissors.jpg')
    embed.add_field(name='Player 1:', value=ctx.author.name)
    embed.add_field(name='Player 2:', value=member.name)
    await ctx.send(embed=embed)
    embed.description = '**Choose an option from below:**'
    player1_msg = await ctx.author.send(embed=embed)
    await player1_msg.add_reaction('🪨')
    await player1_msg.add_reaction('🧻')
    await player1_msg.add_reaction('✂️')
    await message.edit(content='`Game created successfully` *(Check DMs)*')
    check = lambda r, u: u.id == ctx.author.id and str(r.emoji) in "🪨🧻✂️"
    try:
      reaction1, user1 = await bot.wait_for('reaction_add', check=check, timeout=30)
    except asyncio.TimeoutError:
      await message.delete()
      await ctx.send(f"{ctx.author.mention}, {member.mention}: `Game cancelled, timed out.`")
      return 

    player2_msg = await member.send(embed=embed)
    await player2_msg.add_reaction('🪨')
    await player2_msg.add_reaction('🧻')
    await player2_msg.add_reaction('✂️')
    check = lambda r, u: u.id == member.id and str(r.emoji) in "🪨🧻✂️"
    try:
      reaction2, user2 = await bot.wait_for('reaction_add', check=check, timeout=30)
    except asyncio.TimeoutError:
      await message.delete()
      await ctx.send(f"{ctx.author.mention}, {member.mention}: `Game cancelled, timed out.`")
      return
    arr = ['🧻&🪨', '✂️&🧻']
    if str(reaction1.emoji) == str(reaction2.emoji):
      embed = discord.Embed(title='Results', color=ctx.author.top_role.color)
      embed.add_field(name=f'{str(reaction1)} == {str(reaction2)}', value='It''s a Tie!', inline=False)
      embed.set_author(name='Game Over!')
      embed.set_thumbnail(url='https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcS6R63nEBSwQBGBICTHQrcbC9SAd_tdLR9k3w&usqp=CAU')
      embed.set_footer(text='Game made by Younes#5003', icon_url='https://cdn.discordapp.com/avatars/387798722827780108/7b2a3c20de224aa0b0c49856927d2d4a.webp?size=1024')
      await message.delete()
      await ctx.send(embed=embed)
      await ctx.author.send(embed=embed)
      await member.send(embed=embed)
    elif ("&".join([str(reaction1.emoji), str(reaction2.emoji)]) in arr) or (str(reaction1.emoji) == '🪨' and str(reaction2.emoji) == '✂️'):
      embed = discord.Embed(title='Results', color=ctx.author.top_role.color)
      embed.add_field(name=f'{str(reaction1.emoji)} > {str(reaction2.emoji)}', value=f'🥳 {ctx.author.name} Wins! 🥳')
      embed.set_author(name='Game Over!')
      embed.set_thumbnail(url='https://www.pinclipart.com/picdir/big/576-5762132_player-1-wins-clipart.png')
      embed.set_footer(text='Game made by Younes#5003', icon_url='https://cdn.discordapp.com/avatars/387798722827780108/7b2a3c20de224aa0b0c49856927d2d4a.webp?size=1024')
      await message.delete()
      await ctx.send(embed=embed)
      await ctx.author.send(embed=embed)
      await member.send(embed=embed)
    else:
      embed = discord.Embed(title='Results', color=ctx.author.top_role.color)
      embed.add_field(name=f'{str(reaction2.emoji)} > {str(reaction1.emoji)}', value=f'🥳 {member.name} Wins! 🥳')
      embed.set_author(name='Game Over!')
      embed.set_thumbnail(url='http://learnlearn.uk/scratch/wp-content/uploads/sites/7/2018/01/player2png.png')
      embed.set_footer(text='Game made by Younes#5003', icon_url='https://cdn.discordapp.com/avatars/387798722827780108/7b2a3c20de224aa0b0c49856927d2d4a.webp?size=1024')
      await message.delete()
      await ctx.send(embed=embed)
      await ctx.author.send(embed=embed)
      await member.send(embed=embed)

@rps.error
async def rps_error(ctx, error : commands.CommandError):
  if isinstance(error, commands.MissingRequiredArgument):
    await ctx.message.add_reaction('❌')
    embed = discord.Embed(title='Missing Arguments Error', description=':no_entry: - You are missing the required arguments to run this command!', color=0xe74c3c)
    embed.add_field(name='Command:', value='**&rps `[member]`**')
    await ctx.send(embed=embed)
  else:
    await ctx.message.add_reaction('❌')
    embed = discord.Embed(title='Member Not Found Error', description=':no_entry: - Invalid opponent please mention another player!', color=0xe74c3c)
    await ctx.send(embed=embed)
    print(error)

#movie command
@bot.command()
@commands.guild_only()
async def movie(ctx, *, search_term : str):
  response = requests.get("https://imdb-api.com/en/API/SearchAll/k_g8yoa1tc/{}".format("%20".join(search_term.lower().split())))
  json_data = json.loads(response.text)
  if not json_data['results'] or json_data['results'][0]['resultType'] != 'Title':
    await ctx.message.add_reaction('❌')
    embed = discord.Embed(description=':no_entry: - No movies/series were found that match your provided filter(s).!', color=0xe74c3c)
    await ctx.reply(embed=embed, mention_author=False)
  else:
    movie_id = json_data['results'][0]['id']
    url = "https://imdb-api1.p.rapidapi.com/Title/k_g8yoa1tc/{}".format(movie_id)

    headers = {
        'x-rapidapi-host': "imdb-api1.p.rapidapi.com",
        'x-rapidapi-key': "ec2f8ccf8bmshbf1cf334816d19ep12966ejsnbf378abe0c43"
        }

    response = requests.request("GET", url, headers=headers)

    json_data = json.loads(response.text)
    title = json_data['title']
    type = json_data['type']
    year = json_data['year']
    image_url = json_data['image']
    release_date = json_data['releaseDate']
    length = json_data['runtimeStr'] if type == 'Movie' else '{} Seasons'.format(len(json_data['tvSeriesInfo']['seasons']))
    summary = json_data['plot']
    awards = json_data['awards'] if json_data['awards'] else 'N/A'
    directors = json_data['directors'] if json_data['directors'] else 'N/A'
    writers = json_data['writers'] if json_data['writers'] else json_data['tvSeriesInfo']['creators']
    stars = json_data['stars']
    genres = json_data['genres']
    countries = json_data['countries']
    languages = json_data['languages']
    rating = json_data['imDbRating']
    budget = json_data['boxOffice']['budget'].split()[0] if json_data['boxOffice']['budget'] else 'N/A'

    embed = discord.Embed(title=f'{title} ({year}) ({type})', color=ctx.author.top_role.color)
    embed.add_field(name='Stars:', value=stars, inline=False)
    embed.add_field(name='Awards:', value=awards)
    embed.add_field(name='Budget:', value=budget)
    embed.add_field(name='Countries:', value=countries)
    embed.add_field(name='Directors:', value=directors)
    embed.add_field(name='Release Date:', value=release_date)
    embed.add_field(name='Length:', value=length)
    embed.add_field(name='Genres:', value=genres)
    embed.add_field(name='Languages:', value=languages)
    embed.add_field(name='IMDB Rating:', value=rating)
    embed.add_field(name='Summary:', value=summary)
    embed.set_thumbnail(url=image_url)
    embed.set_footer(text=f'Writers: {writers}', icon_url=image_url)

    await ctx.reply(embed=embed, mention_author=False)


@movie.error
async def movie_error(ctx : commands.Context, error : commands.CommandError):
  if isinstance(error, commands.MissingRequiredArgument):
    await ctx.message.add_reaction('❌')
    embed = discord.Embed(title='Missing Arguments Error', description=':no_entry: - You are missing the required arguments to run this command!', color=0xe74c3c)
    embed.add_field(name='Command:', value='**&movie `[movie/serie name]`**')
    await ctx.send(embed=embed)


last_msg = []
@bot.event
async def on_message_delete(message):
  global last_msg
  if not message.author.bot:
    last_msg.append(message)
  await asyncio.sleep(60)
  if len(last_msg) > len(message.guild.text_channels) * 5:
    last_msg.clear()

#snipe command
@bot.command()
@commands.guild_only()
@commands.has_permissions(manage_messages=True)
async def snipe(ctx : commands.Context):
  deleted_messages_in_this_channel = [x for x in last_msg if x.channel.id == ctx.message.channel.id]
  if not deleted_messages_in_this_channel:
    embed = discord.Embed(description=f':no_entry: - There are no messages to snipe!', color=0xe74c3c)
    await ctx.message.add_reaction('❌')
    await ctx.reply(embed=embed, mention_author=False)
  else:
    embed = discord.Embed(title=f'There are {len(deleted_messages_in_this_channel)} messages deleted:', color=0xe74c3c)
    for msg in deleted_messages_in_this_channel:
        full_date = str(msg.created_at)[:-7]
        splitted_date = full_date.split()
        joined_date = ' • '.join(splitted_date)
        embed.add_field(name=f'Message deleted by {msg.author} in `{msg.channel.name}`:', value=f':e_mail: - {msg.content}!\n{joined_date}', inline=False)
    embed.set_footer(text=f'Requested by {ctx.author}', icon_url=ctx.author.avatar_url)
    await ctx.reply(embed=embed, mention_author=False)

@snipe.error
async def snipe_error(ctx : commands.Context, error : commands.CommandError):
  if isinstance(error, commands.MissingPermissions):
    await ctx.message.add_reaction('❌')
    embed = discord.Embed(title='Permission Error', description=':no_entry: - You are missing the required permissions to run this command!', color=0xe74c3c)
    await ctx.send(embed=embed)

#ping command
@bot.command()
@commands.guild_only()
async def ping(ctx):
  await ctx.reply(f'✅ {round(bot.latency * 1000)}ms!', mention_author=False)

#joke command
@bot.command()
@commands.guild_only()
async def joke(ctx, *, contains : str = ''):
  url = 'https://v2.jokeapi.dev/joke/Any?blacklistFlags=nsfw,religious,political,racist,sexist,explicit&type=single&amount=1' if contains == '' else 'https://v2.jokeapi.dev/joke/Any?blacklistFlags=nsfw,religious,political,racist,sexist,explicit&type=single&contains={}&amount=1'.format(contains)
  response = requests.get(url)
  json_data = json.loads(response.text)
  if json_data['error'] != True:
    joke_category = json_data['category']
    joke = json_data['joke']
    embed = discord.Embed(title=f'{joke_category} Joke:', description=joke, color = ctx.author.top_role.color)
    embed.set_footer(text='Request by {}'.format(ctx.author),icon_url=ctx.author.avatar_url)
  else:
    await ctx.message.add_reaction('❌')
    embed = discord.Embed(description=':no_entry: - {} !'.format(json_data['causedBy'][0]), color=0xe74c3c)  
  await ctx.reply(embed=embed, mention_author=False)


#corona command
@bot.command()
@commands.guild_only()
async def corona(ctx, *, country : str = ''):
  url = "https://covid-193.p.rapidapi.com/statistics"
  country = 'Tunisia' if country == '' else country
  querystring = {"country":country}

  headers = {
      'x-rapidapi-host': "covid-193.p.rapidapi.com",
      'x-rapidapi-key': "ec2f8ccf8bmshbf1cf334816d19ep12966ejsnbf378abe0c43"
      }

  response = requests.request("GET", url, headers=headers, params=querystring)

  json_data = json.loads(response.text)
  if json_data['results'] == 0:
    await ctx.message.add_reaction('❌')
    embed = discord.Embed(description=':rolling_eyes: - {} I can\'t find **{}**!'.format(ctx.author.name, country), color=0xe74c3c)
    await ctx.reply(embed=embed, mention_author=False)
  else:
    country = json_data['response'][0]['country']
    url = "https://covid-19-data.p.rapidapi.com/country"

    querystring = {"name":country,"format":"json"}

    headers = {
        'x-rapidapi-host': "covid-19-data.p.rapidapi.com",
        'x-rapidapi-key': "ec2f8ccf8bmshbf1cf334816d19ep12966ejsnbf378abe0c43"
        }

    response = requests.request("GET", url, headers=headers, params=querystring)
    country_code = json.loads(response.text)[0]['code'].lower()
    continent = json_data['response'][0]['continent']
    population = json_data['response'][0]['population']
    new_cases = json_data['response'][0]['cases']['new']
    active_cases = json_data['response'][0]['cases']['active']
    recovered_cases = json_data['response'][0]['cases']['recovered']
    total_cases = json_data['response'][0]['cases']['total']
    new_deaths = json_data['response'][0]['deaths']['new']
    total_deaths = json_data['response'][0]['deaths']['total']
    day = json_data['response'][0]['day']
    embed = discord.Embed(title=f'Corona Statistics in {country} :flag_{country_code}::',
    color=0xe74c3c)
    embed.add_field(name='Continent:', value=continent)
    embed.add_field(name='Country:', value=country)
    embed.add_field(name='Population:', value=population)
    embed.add_field(name='Total Cases:', value=total_cases)
    embed.add_field(name='Active Cases:', value=active_cases)
    embed.add_field(name='New Cases:', value=new_cases)
    embed.add_field(name='Recovered:', value=recovered_cases)
    embed.add_field(name='Total Deaths:', value=total_deaths)
    embed.add_field(name='New Deaths:', value=new_deaths)
    embed.set_author(name=day)
    embed.set_footer(text='Stay safe 🌸')
    await ctx.reply(embed=embed, mention_author=False)

#avatar command
@bot.command()
@commands.guild_only()
async def avatar(ctx, *, member : str = ''):
  if len(member) > 0:
    if '!' in member:
      member = ctx.guild.get_member(int(member[3:-1]))
      embed = discord.Embed(title="Avatar Link",
      url=member.avatar_url,
      color=member.top_role.color)
      embed.set_author(name=member,
      icon_url=member.avatar_url)
      embed.set_image(url=member.avatar_url_as(format='gif') if member.is_avatar_animated() else member.avatar_url_as(format='png'))
      embed.set_footer(text='Requested by {}'.format(ctx.author),
      icon_url=ctx.author.avatar_url)
      await ctx.reply(embed = embed, mention_author=False)
    elif not ctx.guild.get_member_named(member):
      await ctx.message.add_reaction('❌')
      embed = discord.Embed(description=':rolling_eyes: - {} I can\'t find **{}**!'.format(ctx.author.name, member), color=0xe74c3c)
      await ctx.reply(embed=embed, mention_author=False)
    else:
      member = ctx.guild.get_member_named(member)
      embed = discord.Embed(title="Avatar Link",
      url=member.avatar_url,
      color=member.top_role.color)
      embed.set_author(name=member,
      icon_url=member.avatar_url)
      embed.set_image(url=member.avatar_url_as(format='gif') if member.is_avatar_animated() else member.avatar_url_as(format='png'))
      embed.set_footer(text='Requested by {}'.format(ctx.author),
      icon_url=ctx.author.avatar_url)
      await ctx.reply(embed = embed, mention_author=False)
  else:
    member = ctx.author
    embed = discord.Embed(title="Avatar Link",
    url=member.avatar_url,
    color=member.top_role.color)
    embed.set_author(name=member,
    icon_url=member.avatar_url)
    embed.set_image(url=member.avatar_url_as(format='gif') if member.is_avatar_animated() else member.avatar_url_as(format='png'))
    embed.set_footer(text='Requested by {}'.format(member),
    icon_url=member.avatar_url)
    await ctx.reply(embed = embed, mention_author=False)

#say command
@bot.command(description='Sends the provided message.', aliases=['s'])
@commands.guild_only()
async def say(ctx, *, arg):
  await ctx.message.delete()
  await ctx.trigger_typing()
  await ctx.send(arg)

@say.error
async def say_error(ctx : commands.Context, error : commands.CommandError):
  if isinstance(error, commands.MissingRequiredArgument):
    await ctx.message.add_reaction('❌')
    embed = discord.Embed(title='Missing Arguments Error', description=':no_entry: - You are missing the required arguments to run this command!', color=0xe74c3c)
    embed.add_field(name='Command:', value='**&say `[message]`**')
    await ctx.send(embed=embed)

#quote command
@bot.command(description='Returns a random quote.')
@commands.guild_only()
async def quote(ctx):
  quote = get_random_quote().split('|')[0]
  author = get_random_quote().split('|')[1]
  await ctx.message.delete()
  await ctx.trigger_typing()
  embed = discord.Embed(title='Quote:',
  description=quote,
  color=ctx.message.author.top_role.color)
  embed.add_field(name='Author:', value=f':book: *{author}*')
  embed.set_footer(text='Requested by {}'.format(ctx.author), icon_url=ctx.author.avatar_url)
  await ctx.send(embed=embed)

keep_alive()
bot.run(os.getenv('TOKEN'))