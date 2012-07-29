#!/usr/bin/python
# -*- coding: utf-8 -*-
import xbmcplugin
import xbmc
import xbmcgui
import urllib
import urllib2
import sys
import os
import time
import md5
import tempfile
import addoncompat
from BeautifulSoup import BeautifulStoneSoup


try: from sqlite3 import dbapi2 as sqlite
except: from pysqlite2 import dbapi2 as sqlite
    

pluginhandle = int (sys.argv[1])
"""
    PARSE ARGV
"""

class _Info:
    def __init__( self, *args, **kwargs ):
        print "common.args"
        print kwargs
        self.__dict__.update( kwargs )

exec '''args = _Info(%s)''' % (urllib.unquote_plus(sys.argv[2][1:].replace("&", ", ").replace("'","\'").replace('%5C', '%5C%5C')).replace('%A9',u'\xae').replace('%E9',u'\xe9').replace('%99',u'\u2122') , )

"""
    DEFINE
"""
site_dict= {'aetv':'A&E',
            'abc': 'ABC',
            'abcfamily': 'ABC Family',
            'adultswim': 'Adult Swim',
            'amc': 'AMC',
            'bio': 'Biography',
            'bravo': 'Bravo',
            'cartoon': 'Cartoon Network',
            'cbs': 'CBS',
            'thecw': 'CW, The',
            'comedy': 'Comedy Central',
            'crackle': 'Crackle',
            'disney':'Disney',
            'disneyxd':'Disney XD',
            'food': 'Food Network',
            'fox': 'FOX',
            'fx': 'FX',
            'gsn': 'Game Show Network',
            'hgtv': 'HGTV',
            'history': 'History Channel',
            'hub':'Hub, The',
            'lifetime': 'Lifetime',
            'marvel': 'Marvel',
            'marvelkids': 'Marvel Kids',
            'mtv': 'MTV',
            'natgeo': 'National Geographic',
            'natgeowild': 'Nat Geo Wild',
            'nbc': 'NBC',
            'nickteen': 'Nick Teen',
            'nicktoons': 'Nick Toons',
            'nick': 'Nickelodeon',
            'oxygen': 'Oxygen',
            'pbs': 'PBS',
            'pbskids': 'PBS Kids',
            'spike': 'Spike',
            'syfy': 'SyFy',
            'tbs': 'TBS',
            'tnt': 'TNT',
            'tvland': 'TV Land',
            'usa': 'USA',
            'vh1': 'VH1',
            'thewbkids': 'WB Kids, The',
            'thewb': 'WB, The',
            }

site_descriptions= {'aetv': "A&E is Real Life. Drama.  Now reaching more than 99 million homes, A&E is television that you can't turn away from; where unscripted shows are dramatic and scripted dramas are authentic.  A&E offers a diverse mix of high quality entertainment ranging from the network's original scripted series to signature non-fiction franchises, including the Emmy-winning \'Intervention,\' \'Dog The Bounty Hunter,\' \'Hoarders,\' \'Paranormal State\' and \'Criss Angel Mindfreak,\' and the most successful justice shows on cable, including \'The First 48\' and \'Manhunters.\'  The A&E website is located at www.aetv.com.",
                    'abc': "ABC Television Network provides broadcast programming to more than 220 affiliated stations across the U.S.  The Network encompasses ABC News, which is responsible for news programming on television and other digital platforms; ABC Entertainment Group, a partnership between ABC Studios and ABC Entertainment responsible for the network's primetime and late-night entertainment programming; ABC Daytime, producer of the network's successful cache of daytime programming; as well as ABC Kids, the Network's children's programming platform. ABC's multiplatform business initiative includes the Interactive Emmy Award-winning broadband player on ABC.com.",
                    'abcfamily': "ABC Family's programming is a combination of network-defining original series and original movies, quality acquired series and blockbuster theatricals. ABC Family features programming reflecting today's families, entertaining and connecting with adults through relatable stories about today's relationships, told with a mix of diversity, passion, humor and heart. Targeting Millennial viewers ages 14-34, ABC Family is advertiser supported.",
                    'adultswim': "Cartoon Network (CartoonNetwork.com), currently seen in more than 97 million U.S. homes and 166 countries around the world, is Turner Broadcasting System, Inc.'s ad-supported cable service now available in HD offering the best in original, acquired and classic entertainment for youth and families.  Nightly from 10 p.m. to 6 a.m. (ET, PT), Cartoon Network shares its channel space with Adult Swim, a late-night destination showcasing original and acquired animated and live-action programming for young adults 18-34 ",
                    'amc': "AMC reigns as the only cable network in history to ever win the Emmy' Award for Outstanding Drama Series three years in a row, as well as the Golden Globe' Award for Best Television Series - Drama for three consecutive years.  Whether commemorating favorite films from every genre and decade or creating acclaimed original programming, the AMC experience is an uncompromising celebration of great stories.  AMC's original stories include 'Mad Men,' 'Breaking Bad,' 'The Walking Dead,' 'The Killing' and 'Hell on Wheels.'  AMC further demonstrates its commitment to the art of storytelling with AMC's Docu-Stories, a slate of unscripted original series, as well as curated movie franchises like AMC's Can't Get Enough and AMC's Crazy About.  Available in more than 97 million homes (Source: Nielsen Media Research), AMC is owned and operated by AMC Networks Inc. and its sister networks include IFC, Sundance Channel and WE tv.  AMC is available across all platforms, including on-air, online, on demand and mobile.  AMC: Story Matters HereSM.",
                    'bio': "At Bio, we prove that the truth about people is always more entertaining than fiction. Bio is about real people and their real lives: up close and personal, gritty and provocative, always unfiltered. Bio original series uncover the real drama in people stories: everyday situations with a twist; celebrities going off-script; people-centric crime stories and paranormal events. In addition to being the exclusive home to the Emmy-Award winning Biography' series, Bio's dynamic blend of original and acquired series includes The Final 24, Psychic Investigators and the upcoming William Shatner hosted talk show, Shatner's Raw Nerve. One of the fastest growing cable networks in 2006, the 24-hour network is now available in more than 47 million households. The Bio web site is located at www.bio.tv. ",
                    'bravo': "With more breakout stars and critically-acclaimed original series than any other network on cable, Bravo's original programming - from hot cuisine to haute couture - delivers the best in food, fashion, beauty, design and pop culture to the most engaged and upscale audience in cable. Consistently one of the fastest growing top 20 ad-supported cable entertainment networks, Bravo continues to translate buzz into reality with critically-acclaimed breakout creative competition and docu-series, including the Emmy and James Beard Award-winning No. 1 food show on cable \"Top Chef,\" two-time Emmy Award winner \"Kathy Griffin: My Life on the D-List,\" the 14-time Emmy nominated \"Inside the Actors Studio,\" the hit series \"Shear Genius,\" \"Top Chef Masters,\" \"Flipping Out,\" \"The Rachel Zoe Project,\" \"Tabatha's Salon Takeover,\" \"Million Dollar Listing,\" \"The Millionaire Matchmaker,\" and the watercooler sensation that is \"The Real Housewives\" franchise. Bravo reaches its incredibly unique audience through every consumer touch point and across all platforms on-air, online and on the go, providing the network\'s highly-engaged fans with a menu of options to experience the network in a four-dimensional manner. Bravo is a program service of NBC Universal Cable Entertainment, a division of NBC Universal one of the world\'s leading media and entertainment companies in the development, production, and marketing of entertainment, news and information to a global audience. Bravo has been an NBC Universal cable network since December 2002 and was the first television service dedicated to film and the performing arts when it launched in December 1980. For more information visit www.bravotv.com",
                    'cartoon': "Cartoon Network (CartoonNetwork.com), currently seen in more than 99 million U.S. homes and 166 countries around the world, is Turner Broadcasting System, Inc.'s ad-supported cable service offering the best in original, acquired and classic animated entertainment for kids and families. Overnight from 10 p.m.-6 a.m. (ET, PT) Monday -Sunday, Cartoon Network shares its channel space with [adult swim], a late-night destination showcasing original and acquired animation for young adults 18-34.",
                    'cbs': "CBS was established in 1928, when founder William Paley purchased 16 independent radio stations and christened them the Columbia Broadcast System. Today, with more than 200 television stations and affiliates reaching virtually every home in the United States, CBS's total primetime network lineup is watched by more than 130 million people a week during the 2010/2011 season. The Network has the #1 drama/scripted program, NCIS; #1 sitcom, TWO AND A HALF MEN; #1 newsmagazine, 60 MINUTES; and #1 daytime drama, THE YOUNG AND THE RESTLESS. Its programming arms include CBS Entertainment, CBS News and CBS Sports.",
                    'thecw': "The CW Network was formed as a joint venture between Warner Bros. Entertainment and CBS Corporation. The CW is America's fifth broadcast network and the only network targeting women 18-34. The network's primetime schedule includes such popular series as America's Next Top Model, Gossip Girl, Hart of Dixie, 90210, The Secret Circle, Supernatural, Ringer, Nikita, One Tree Hill and The Vampire Diaries.",
                    'comedy': "COMEDY CENTRAL, the #1 brand in comedy, is available to over 99 million viewers nationwide and is a top-rated network among men ages 18-24 and 18-34 and adults ages 18-49.  With on-air, online and on-the-go mobile technology, COMEDY CENTRAL gives its audience access to the cutting-edge, laugh-out-loud world of comedy wherever they go.  Hit series include Tosh.0, Workaholics, Futurama, Key & Peele, Ugly Americans and the Emmy' and Peabody' Award-winning series The Daily Show with Jon Stewart, The Colbert Report and South Park.  COMEDY CENTRAL is also involved in producing nationwide stand-up tours, boasts its own record label and operates one of the most successful home entertainment divisions in the industry.  COMEDY CENTRAL is owned by, and is a registered trademark of Comedy Partners, a wholly-owned unit of Viacom Inc. (NASDAQ: VIA and VIAB).  For more information visit COMEDY CENTRAL's press Web site at www.cc.com/press or the network's consumer site at www.comedycentral.com and follow us on Twitter @ComedyCentralPR for the latest in breaking news updates, behind-the-scenes information and photos.",
                    'crackle': "Crackle, Inc. is a multi-platform video entertainment network and studio that distributes full length, uncut, movies, TV shows and original programming in our users favorite genres � like comedy, action, crime, horror, Sci-Fi, and thriller. Crackles channels and shows reach a global audience across the Internet, in the living room, and on devices including a broad range of Sony electronics.",
                    'disney':'Disney',
                    'disneyxd':'Disney XD',
                    'food': "FOOD NETWORK (www.foodnetwork.com) is a unique lifestyle network and Web site that strives to be way more than cooking.  The network is committed to exploring new and different ways to approach food - through pop culture, competition, adventure, and travel - while also expanding its repertoire of technique-based information. Food Network is distributed to more than 96 million U.S. households and averages more than seven million Web site users monthly. With headquarters in New York City and offices in Atlanta, Los Angeles, Chicago, Detroit and Knoxville, Food Network can be seen internationally in Canada, Australia, Korea, Thailand, Singapore, the Philippines, Monaco, Andorra, Africa, France, and the French-speaking territories in the Caribbean and Polynesia. Scripps Networks Interactive (NYSE: SNI), which also owns and operates HGTV (www.hgtv.com), DIY Network (www.diynetwork.com), Great American Country (www.gactv.com) and FINE LIVING (www.fineliving.com), is the manager and general partner.",
                    'fox': "Fox Broadcasting Company is a unit of News Corporation and the leading broadcast television network among Adults 18-49. FOX finished the 2010-2011 season at No. 1 in the key adult demographic for the seventh consecutive year ' a feat that has never been achieved in broadcast history ' while continuing to dominate all network competition in the more targeted Adults 18-34 and Teen demographics. FOX airs 15 hours of primetime programming a week as well as late-night entertainment programming, major sports and Sunday morning news.",
                    'fx': "FX is News Corp.'s flagship general entertainment basic cable network. Launched in 1994, FX is carried in more than 97 million homes and provides a slate of standout original drama series, including Sons of Anarchy, Justified and American Horror Story in addition the comedies It's Always Sunny in Philadelphia, Archer, The League, Louie, Wilfred and Unsupervised. Its diverse schedule includes box-office hits from 20th Century Fox and other major studios, as well as an impressive roster of acquired hit series. FX ranks as the #7 basic cable network in primetime (8-11PM) among P18-49, FX's target demographic. (Most Current thru 10/14/11 among 94 Measured Networks)",
                    'gsn': "GSN is a multimedia entertainment company that offers original and classic game programming and competitive entertainment via its 75-million subscriber television network and online game sites.  GSN's cross-platform content gives game lovers the opportunity to win cash and prizes, whether through GSN's popular TV game shows or through GSN Digital's free casual games, mobile and social games, and cash competitions.  GSN is distributed throughout the U.S., Caribbean and Canada by all major cable operators, satellite providers and telcos.  GSN and its subsidiary, WorldWinner.com, Inc., are owned by DIRECTV and Sony Pictures Entertainment.  For further information, visit GSN at www.gsn.com.",
                    'hgtv': "HGTV makes everyone feel at home everywhere - no matter where they live, work or play. Providing a wide range of lifestyle entertainment that showcases practical advice and fresh ideas from experts in design, architecture, building/remodeling, real estate and more, HGTV inspires viewers to reinvent and transform their own communities, workplaces and shared spaces. Through programming that highlights the authentic stories and relevant situations that impact the design, remodeling, landscaping, buying or selling of a home, HGTV gives viewers a peek into the lives, relationships and creative passions of the human family. In 2010, HGTV's primetime series premieres will include: The Outdoor Room; The Antonio Treatment; Marriage Under Construction; Selling New York; Destination Design; Curb Appeal: The Block; and Design School. Returning primetime favorites include: House Hunters International; HGTV Design Star; Divine Design; Dear Genevieve; and Color Splash. The network's weekend morning lineup offers an entertaining twist on \"do it yourself\" with such popular series as Carter Can, Don't Sweat It, Holmes on Homes, Hammer Heads and Over Your Head. Now available in more than 98 million homes, HGTV is part of the Scripps Networks portfolio of lifestyle-oriented cable networks which includes Food Network, DIY, The Cooking Channel (formerly FLN) and GAC-Great American Country. Viewers can find more of what they love about HGTV at HGTV.com, which offers thousands of photos, gardening and decorating ideas, interactive design tools, easy-to-make projects, videos of new or classic programs and more.",
                    'history': "HISTORY and HISTORY HD are the leading destinations for revealing, award-winning original non-fiction series and event-driven specials that connect history with viewers in an informative, immersive and entertaining manner across multiple platforms. Programming covers a diverse variety of historical genres ranging from military history to contemporary history, technology to natural history, as well as science, archaeology and pop culture. Among the network's program offerings are hit series such as Ax Men, Battle 360, How The Earth Was Made, Ice Road Truckers, Pawn Stars and The Universe, as well as acclaimed specials including 102 Minutes That Changed America, 1968 with Tom Brokaw, King, Life After People, Nostradamus: 2012 and Star Wars: The Legacy Revealed. HISTORY has earned four Peabody Awards, seven Primetime Emmy' Awards, 12 News & Documentary Emmy' Awards and received the prestigious Governor's Award from the Academy of Television Arts & Sciences for the network's Save Our History' campaign dedicated to historic preservation and history education. Take a Veteran to School Day is the network's latest initiative connecting America's schools and communities with veterans from all wars. The HISTORY web site, located at www.history.com, is the definitive historical online source that delivers entertaining and informative content featuring broadband video, interactive timelines, maps, games, podcasts and more.",
                    'hub':"The Hub, a multi-platform joint venture between Discovery Communications (NASDAQ: DISCA, DISCB, DISCK) and Hasbro, Inc. (NYSE: HAS), is a cable and satellite television network featuring original programming as well as content from Discovery's library of award-winning children's educational programming; from Hasbro's rich portfolio of entertainment and educational properties built during the past 90 years; and from leading third-party producers worldwide. The Hub lineup includes animated and live-action series, specials and game shows, and the network extends its content online. The Hub launched October 10, 2010 (10-10-10) in approximately 60 million U.S. households.",
                    'lifetime': "A leading force in the entertainment industry, Lifetime Television is the highest-rated women's network, followed only by its sister channel, Lifetime Movie Network. Upon its 1984 launch, Lifetime quickly established itself as a pioneer in the growing cable universe to become the preeminent television destination and escape for women and has long been the number one female-targeted network on all of basic cable among Women 18-49, Women 25-54 and Women 18+. The Network, one of television's most widely distributed outlets, is currently seen in nearly 98 million households nationwide. Lifetime is synonymous with providing critically acclaimed, award-winning and popular original programming for women that spans movies and miniseries, dramas, comedies and reality series. In continuing this tradition, the Network has aggressively expanded its original programming slate, and, for the 2009-10 season, has amassed the most powerful line-up in Company history.",
                    'marvel': 'Marvel started in 1939 as Timely Publications, and by the early 1950s had generally become known as Atlas Comics. Marvel\'s modern incarnation dates from 1961, the year that the company launched Fantastic Four and other superhero titles created by Stan Lee, Jack Kirby, Steve Ditko, and others. Marvel counts among its characters such well-known properties as Spider-Man, the X-Men, the Fantastic Four, Iron Man, the Hulk, Thor, Captain America and Daredevil; antagonists such as the Green Goblin, Magneto, Doctor Doom, Galactus, and the Red Skull. Most of Marvel\'s fictional characters operate in a single reality known as the Marvel Universe, with locations that mirror real-life cities such as New York, Los Angeles and Chicago.',
                    'marvelkids': 'Marvel started in 1939 as Timely Publications, and by the early 1950s had generally become known as Atlas Comics. Marvel\'s modern incarnation dates from 1961, the year that the company launched Fantastic Four and other superhero titles created by Stan Lee, Jack Kirby, Steve Ditko, and others. Marvel counts among its characters such well-known properties as Spider-Man, the X-Men, the Fantastic Four, Iron Man, the Hulk, Thor, Captain America and Daredevil; antagonists such as the Green Goblin, Magneto, Doctor Doom, Galactus, and the Red Skull. Most of Marvel\'s fictional characters operate in a single reality known as the Marvel Universe, with locations that mirror real-life cities such as New York, Los Angeles and Chicago.',
                    'mtv': "MTV is Music Television. It is the music authority where young adults turn to find out what's happening and what's next in music and popular culture. MTV reaches 412 million households worldwide, and is the #1 Media Brand in the world. Only MTV can offer the consistently fresh, honest, groundbreaking, fun and inclusive youth-oriented programming found nowhere else in the world. MTV is a network that transcends all the clutter, reaching out beyond barriers to everyone who's got eyes, ears and a television set.",
                    'natgeo': "Critically acclaimed non-fiction. Network providing info-rich entertainment that changes the way you see the world.  A trusted source for more than 100 years, National Geographic provides NGC with unique access to the most respected scientists, journalists and filmmakers, resulting in innovative and contemporary programming of unparalleled quality.  NGC HD continues to provide spectacular imagery that National Geographic is known for in stunning high-definition.  A leader on the digital landscape, NGC HD is one of the top five HD networks and is the #1 channel viewers would most like to see in high definition for the fourth year in a row.  Additionally, the channel received some of the highest ratings in key categories, such as 'high quality,' 'information' and 'favorite' in the prestigious benchmark study among all 55 measured cable and broadcast networks. In addition, NGC VOD is a category leader. Building on its success as one of the fastest-growing cable networks year-to-year in ratings and distribution since launching in January 2001, NGC now reaches more than 70 million homes, with carriage on all major cable and satellite television providers.  Highlighted programming in 2010 includes: New episodes of Expedition Great White, the popular series, Taboo and Border Wars.  In addition, new seasons of series' WORLD'S TOUGHEST FIXES and LOCKED UP ABROAD.  2010 specials include DRUGS, INC., LOST GOLD OF THE DARK AGES and GREAT MIGRATIONS  For more information, please visit www.natgeotv.com.",
                    'natgeowild': "Experience the best, most intimate encounters with wildlife ever seen on television.  Backed by its unparallel reputation and blue chip programming, Nat Geo Wild brings viewers documentaries entirely focused on the animal kingdom and the world it inhabits.  From the most remote environments, to the forbidding depths of our oceans, to the protected parks in our backyards, Nat Geo Wild uses spectacular cinematography and intimate storytelling to take viewers on unforgettable journeys into the wild world.  Nat Geo Wild launched in August 2006 and is now available in Hong Kong, Singapore, the U.K., Australia, Latin America, France, Italy, Portugal, Turkey and other territories in Europe.  Nat Geo Wild HD launched in the U.K. in March 2009 and is also available in Poland.  Additional launches are expected globally.",
                    'nbc': "NBC Entertainment develops and schedules programming for the network's primetime, late-night, and daytime schedules. NBC's quality programs and balanced lineup have earned the network critical acclaim, numerous awards, and ratings success. The network has earned more Emmy Awards than any network in television history. NBC's roster of popular scripted series includes critically acclaimed comedies like Emmy winners The Office, starring Steve Carell, and 30 Rock, starring Alec Baldwin and Tina Fey. Veteran, award-winning dramas on NBC include Law & Order: SVU, Chuck, and Friday Night Lights. Unscripted series for NBC include the hits The Biggest Loser, Celebrity Apprentice, and America's Got Talent. NBC's late-night story is highlighted by The Tonight Show with Jay Leno, Late Night with Jimmy Fallon, Last Call with Carson Daly, and Saturday Night Live. NBC Daytime's Days of Our Lives consistently finishes among daytime's top programs in the valuable women 18-34 category. Saturday mornings the network broadcasts Qubo on NBC, a three-hour block that features fun, entertaining, and educational programming for kids, including the award-winning, 3-D animated series Veggie Tales.",
                    'nickteen': "Launched in April 2002, TeenNick (formerly named The N) features 24-hours of teen programming. Our award-winning and original programming, including Degrassi: The Next Generation, Beyond the Break, The Best Years and The Assistants, presents sharp and thoughtful content that focuses on the real life issues teens face every day. On our Emmy winning website, www.Teennick.com, fans get complete access to behind-the-scenes interviews, pictures and videos, plus a robust community of 2 million members who interact with message boards, user profiles and blogs. TeenNick'۪s broadband channel, The Click, features full-length episodes of the network'۪s hit original series along with outtakes, sneak peeks and webisodes of TeenNick series created exclusively for broadband. The Click provides teens with the ability to create video mash-ups and watch, comment on and share content from their favorite TeenNick shows with all of their friends, wherever they go.",
                    'nicktoons': "Nicktoons offers 24 hours of animated programming that includes Wolverine and the X-Men, Iron Man: Armored Adventures, Fantastic Four: World's Greatest Heroes, Speed Racer: The Next Generation, Kappa Mikey and the Nickelodeon Animation Festival, as well as a roster of hits that have defined kids' and animation lovers' TV, including Avatar: The Last Airbender, Danny Phantom, SpongeBob SquarePants, The Fairly OddParents and The Adventures of Jimmy Neutron, Boy Genius.  It currently reaches 54 million homes via cable, digital cable and satellite, and can be seen on Cablevision, Charter Communications, Comcast Cable, Cox Communications, DirecTV, DISH Network and Time Warner Cable.  Nicktoons is part of the MTV Networks expanded suite of channels available for digital distribution.",
                    'nick': "Nickelodeon, now in its 31st year, is the number-one entertainment brand for kids. It has built a diverse, global business by putting kids first in everything it does. The company includes television programming and production in the United States and around the world, plus consumer products, online, recreation, books and feature films. Nickelodeon's U.S. television network is seen in more than 100 million households and has been the number-one-rated basic cable network for 16 consecutive years.",
                    'oxygen': "Oxygen Media is a multiplatform lifestyle brand that delivers relevant and engaging content to young women who like to \"live out loud.\" Oxygen is rewriting the rulebook for women's media by changing how the world sees entertainment from a young woman's point of view.  Through a vast array of unconventional and original content including \"Bad Girls Club,\" \"Dance Your Ass Off\" and \"Tori & Dean: Home Sweet Hollywood,\" the growing cable network is the premier destination to find unique and groundbreaking unscripted programming.   A social media trendsetter, Oxygen is a leading force in engaging the modern young woman, wherever they are, with popular features online including OxygenLive, shopOholic, makeOvermatic, tweetOverse and hormoneOscope.  Oxygen is available in 76 million homes and online at www.oxygen.com, or on mobile devices at wap.oxygen.com.  Oxygen Media is a service of NBC Universal.",
                    'pbs': "PBS and our member stations are America\'s largest classroom, the nation\'s largest stage for the arts and a trusted window to the world. In addition, PBS's educational media helps prepare children for success in school and opens up the world to them in an age-appropriate way.",
                    'pbskids': 'PBS Kids is the brand for children\'s programming aired by the Public Broadcasting Service (PBS) in the United States founded in 1993. It is aimed at children ages 2 to 13.',
                    'spike': "Spike TV knows what guys like. The brand speaks to the bold, adventuresome side of men with action-packed entertainment, including a mix of comedy, blockbuster movies, sports, innovative originals and live events. Popular shows like The Ultimate Fighter, TNA iMPACT!, Video Game Awards, DEA, MANswers, MXC, and CSI: Crime Scene Investigation, plus the Star Wars and James Bond movie franchises, position Spike TV as the leader in entertainment for men.",
                    'syfy': "Syfy is a media destination for imagination-based entertainment. With year round acclaimed original series, events, blockbuster movies, classic science fiction and fantasy programming, a dynamic Web site (www.Syfy.com), and a portfolio of adjacent business (Syfy Ventures), Syfy is a passport to limitless possibilities. Originally launched in 1992 as SCI FI Channel, and currently in 95 million homes, Syfy is a network of NBC Universal, one of the world's leading media and entertainment companies. Syfy. Imagine greater.",
                    'tbs': "TBS, a division of Turner Broadcasting System, Inc., is television's top-rated comedy network and is available in 100.1 million households.  It serves as home to such original comedy series as My Boys, Neighbors from Hell, Are We There Yet? and Tyler Perry's House of Payne and Meet the Browns; the late-night hit Lopez Tonight, starring George Lopez, and the upcoming late-night series starring Conan O'Brien; hot contemporary comedies like Family Guy and The Office; specials like Funniest Commercials of the Year; special events, including star-studded comedy festivals in Chicago; blockbuster movies; and hosted movie showcases.",
                    'tnt': "TNT, one of cable's top-rated networks, is television's destination for drama.  Seen in 99.6 million households, the network is home to such original series as The Closer, starring Kyra Sedgwick; Leverage, starring Timothy Hutton; and Dark Blue, starring Dylan McDermott; the upcoming Rizzoli & Isles, starring Angie Harmon and Sasha Alexander; Memphis Beat, with Jason Lee; Men of a Certain Age, with Ray Romano, Andre Braugher and Scott Bakula; and Southland, from Emmy'-winning producer John Wells (ER).  TNT also presents such powerful dramas as Bones, Supernatural, Las Vegas, Law & Order, CSI: NY, Cold Case and Numb3rs; broadcast premiere movies; compelling primetime specials, such as the Screen Actors Guild Awards'; and championship sports coverage, including NASCAR and the NBA.  The NCAA men's basketball tournament will appear on TNT beginning in 2011.  TNT is available in high-definition.",
                    'tvland': "TV Land is dedicated to presenting the best in entertainment on all platforms for consumers in their 40s. Armed with a slate of original programming, acquired classic shows, hit movies and fullservice website, TV Land is now seen in over 98 million U.S. homes. TV Land PRIME is TV Land's prime time programming destination designed for people in their mid-forties and the exclusive home to the premieres of the network's original programming, contemporary television series acquisitions and movies.",
                    'usa': "USA Network is cable television's leading provider of original series and feature movies, sports events, off-net television shows, and blockbuster theatrical films. USA Network is seen in over 88 million U.S. homes. The USA Network web site is located at www.usanetwork.com. USA Network is a program service of NBC Universal Cable a division of NBC Universal, one of the world's leading media and entertainment companies in the development, production and marketing of entertainment, news and information to a global audience.",
                    'vh1': "VH1 connects viewers to the music, artists and pop culture that matter to them most with series, specials, live events, exclusive online content and public affairs initiatives. VH1 is available in 90 million households in the U.S. VH1 also has an array of digital services including VH1 Classic, VH1 Soul and VSPOT, VH1's broadband channel. Connect with VH1 at www.VH1.com.",
                    'thewbkids': 'The KidsWB Collection of Scooby-Doo, Looney Toons, Batman: The Brave and the Bold, Hanna-Barbera, DC and Warner stars under one roof.',
                    'thewb': "TheWB.com is the 1 fan site for shows targeted to adults 18-34. Whether it's the familiar ones you love or the new and the original series made only for the web, TheWB.com paves the way as a premium video entertainment destination. It's TV online. On TheWB.com, you can watch full-length episodes of One Tree Hill, The O.C., Buffy the Vampire Slayer, Gilmore Girls, Everwood, Smallville, Friends, Pushing Daisies, Chuck, Jack & Bobby, Angel and Veronica Mars. Plus, it has additional features that include community and message boards, extensive photo galleries, games and downloadable features that allow you to have a deeper relationship with these and other television shows. TheWB.com also offers a line-up of original series made exclusively for the web from some of the top producers in Hollywood, including Sorority Forever, Rich Girl Poor Girl, Childrens' Hospital and the upcoming Rockville CA. TheWB.com is free, ad-supported and available anytime in the U.S. Thank you for your viewership!",
                    }

addoncompat.get_revision()
pluginpath = addoncompat.get_path()
db_path = 'special://home/addons/script.module.free.cable.database/lib/'

db_file = os.path.join(xbmc.translatePath(db_path),'shows.db')
cachepath = os.path.join(xbmc.translatePath(pluginpath),'resources','cache')
imagepath = os.path.join(xbmc.translatePath(pluginpath),'resources','images')
fanartpath = os.path.join(xbmc.translatePath(pluginpath),'resources','FAimages')
plugin_icon = os.path.join(xbmc.translatePath(pluginpath),'icon.png')
plugin_fanart = os.path.join(xbmc.translatePath(pluginpath),'fanart.jpg')
fav_icon = os.path.join(xbmc.translatePath(pluginpath),'fav.png')
all_icon = os.path.join(xbmc.translatePath(pluginpath),'allshows.png')

"""
    GET SETTINGS
"""

settings={}
#settings general
quality = ['200', '400', '600', '800', '1000', '1200', '1400', '1600', '2000', '2500', '3000', '100000']
selectquality = int(addoncompat.get_setting('quality'))
settings['quality'] = quality[selectquality]
settings['enableproxy'] = addoncompat.get_setting('us_proxy_enable')
settings['enablesubtitles'] = addoncompat.get_setting('enablesubtitles')

def get_series_id(seriesdata,seriesname):
    shows = BeautifulStoneSoup(seriesdata, convertEntities=BeautifulStoneSoup.HTML_ENTITIES).findAll('series')
    names = list(BeautifulStoneSoup(seriesdata, convertEntities=BeautifulStoneSoup.HTML_ENTITIES).findAll('seriesname'))
    if len(names) > 1:
        select = xbmcgui.Dialog()
        ret = select.select(seriesname, [name.string for name in names])
        if ret <> -1:
            seriesid = shows[ret].find('seriesid').string
    else:
        seriesid = shows[0].find('seriesid').string
    return seriesid

def tv_db_series_lookup(seriesname,manualSearch=False):
    tv_api_key = '03B8C17597ECBD64'
    mirror = 'http://thetvdb.com'
    banners = 'http://thetvdb.com/banners/'
    series_lookup = 'http://www.thetvdb.com/api/GetSeries.php?seriesname='+urllib.quote_plus(seriesname)
    seriesdata = getURL(series_lookup)
    try: seriesid = get_series_id(seriesdata,seriesname)
    except:
        if manualSearch:
            keyb = xbmc.Keyboard(seriesname, 'Manual Search')
            keyb.doModal()
            if (keyb.isConfirmed()):
                    series_lookup = 'http://www.thetvdb.com/api/GetSeries.php?seriesname='+urllib.quote_plus(keyb.getText())
                    seriesid = getURL(series_lookup)
                    try: seriesid = get_series_id(seriesid,seriesname)
                    except:
                        print 'manual search failed'
                        return False
        else:
            return False
    series_xml = mirror+('/api/%s/series/%s/en.xml' % (tv_api_key, seriesid))
    series_xml = getURL(series_xml)
    tree = BeautifulStoneSoup(series_xml, convertEntities=BeautifulStoneSoup.HTML_ENTITIES)
    #print tree.prettify()
    try:
        first_aired = tree.find('firstaired').string
        date = first_aired
        year = int(first_aired.split('-')[0])
    except:
        print '%s - Air Date Failed' % seriesname
        first_aired = None
        date = None
        year = None
    try: genres = tree.find('genre').string
    except:
        print '%s - Genre Failed' % seriesname
        genres = None
    try: plot = tree.find('overview').string
    except:
        print '%s - Plot Failed' % seriesname
        plot = None
    try: actors = tree.find('actors').string
    except:
        print '%s - Actors Failed' % seriesname
        actors = None
    try: rating = float(tree.find('rating').string)
    except:
        print '%s - Rating Failed' % seriesname
        rating = None
    try: TVDBbanner = banners + tree.find('banner').string
    except:
        print '%s - Banner Failed' % seriesname
        TVDBbanner = None
    try: TVDBfanart = banners + tree.find('fanart').string
    except:
        print '%s - Fanart Failed' % seriesname
        TVDBfanart = None
    try: TVDBposter = banners + tree.find('poster').string
    except:
        print '%s - Poster Failed' % seriesname
        TVDBposter = None
    try: IMDB_ID = tree.find('imdb_id').string
    except:
        print '%s - IMDB_ID Failed' % seriesname
        IMDB_ID = None
    try: runtime = tree.find('runtime').string
    except:
        print '%s - Runtime Failed' % seriesname
        runtime = None
    try: Airs_DayOfWeek = tree.find('airs_dayofweek').string
    except:
        print '%s - Airs_DayOfWeek Failed' % seriesname
        Airs_DayOfWeek = None
    try: Airs_Time = tree.find('airs_time').string
    except:
        print '%s - Airs_Time Failed' % seriesname
        Airs_Time = None
    try: status = tree.find('status').string
    except:
        print '%s - status Failed' % seriesname
        status = None
    try: network = tree.find('network').string
    except:
        print '%s - Network Failed' % seriesname
        network = None
    return [seriesid,IMDB_ID,TVDBbanner,TVDBposter,TVDBfanart,first_aired,date,year,actors,genres,network,plot,runtime,rating,Airs_DayOfWeek,Airs_Time,status]

def load_db():
    #if os.path.exists(db_file):
    #    os.remove(db_file)
    if not os.path.exists(db_file):
        create_db()
        refresh_db()
    #else:
    #    refresh_db()
    conn = sqlite.connect(db_file)
    c = conn.cursor()
    return c.execute('select * from shows order by series_title')

def load_showlist(favored=False):
    shows = load_db()
    for series_title,mode,sitemode,url,TVDB_ID,IMDB_ID,TVDBbanner,TVDBposter,TVDBfanart,first_aired,date,year,actors,genres,network,plot,runtime,rating,Airs_DayOfWeek,Airs_Time,status,has_full_episodes,favor,hide in shows:
        if addoncompat.get_setting(mode) == 'false':
            continue
        elif hide:
            continue
        elif favored and not favor:
            continue
        thumb=os.path.join(imagepath,mode+'.png')
        fanart=''
        infoLabels={}
        if TVDBfanart:
            fanart=TVDBfanart
        else:
            if args.__dict__.has_key('fanart'): fanart = args.fanart
            else: fanart=''
        if TVDBbanner:
            thumb=TVDBbanner
        elif TVDBposter:
            thumb=TVDBposter
        infoLabels['Title']=series_title.encode('utf-8', 'ignore')
        infoLabels['TVShowTitle']=series_title.encode('utf-8', 'ignore')
        prefixplot=''
        if network<>None:
            if site_dict[mode] <> network:
                prefixplot+='Network: %s' % network
                prefixplot+='\n'
                prefixplot+='Station: %s' % site_dict[mode]
                prefixplot+='\n'
            else:
                prefixplot+='Station: %s' % site_dict[mode]
                prefixplot+='\n'
        else:
            prefixplot+='Station: %s' % site_dict[mode]
            prefixplot+='\n'   
        if Airs_DayOfWeek<>None and Airs_Time<>None:
            prefixplot+='Airs: %s @ %s' % (Airs_DayOfWeek,Airs_Time)
            prefixplot+='\n'
        if status<>None:
            prefixplot+='Status: %s' % status
            prefixplot+='\n'
        if prefixplot <> '':
            prefixplot+='\n'
        if plot<>None:
            infoLabels['Plot']=prefixplot.encode('utf-8', 'ignore')+plot.encode('utf-8', 'ignore')
        else:
            infoLabels['Plot']=prefixplot
        if date: infoLabels['date']=date
        if first_aired<>None: infoLabels['aired']=first_aired
        if year<>None: infoLabels['Year']=year
        if actors<>None:
            actors = actors.encode('utf-8', 'ignore').strip('|').split('|')
            if actors[0] <> '':
                infoLabels['cast']=actors
        if genres<>None: infoLabels['genre']=genres.encode('utf-8', 'ignore').replace('|',',').strip(',')
        if network<>None: infoLabels['studio']=network.encode('utf-8', 'ignore')
        if runtime<>None: infoLabels['duration']=runtime
        if rating<>None: infoLabels['rating']=rating
        addShow(series_title, mode, sitemode, url, thumb, fanart,TVDBposter, infoLabels,favor=favor,hide=hide)

def lookup_db(series_title,mode,submode,url,forceRefresh=False):
    #print 'Looking Up: %s for %s' % (series_title,mode)
    conn = sqlite.connect(db_file)
    conn.text_factory = str
    c = conn.cursor()
    checkdata = c.execute('select * from shows where series_title=? and mode=? and submode =?', (series_title,mode,submode)).fetchone()
    if checkdata and not forceRefresh:
        if checkdata[3] <> url:
            c.execute("update shows set url=? where series_title=? and mode=? and submode =?", (url,series_title,mode,submode))
            conn.commit()
            return c.execute('select * from shows where series_title=? and mode=? and submode =?', (series_title,mode,submode)).fetchone()
        else:
            return checkdata
    else:
        tvdb_data = tv_db_series_lookup(series_title,manualSearch=forceRefresh)
        if tvdb_data:
            TVDB_ID,IMDB_ID,TVDBbanner,TVDBposter,TVDBfanart,first_aired,date,year,actors,genres,network,plot,runtime,rating,Airs_DayOfWeek,Airs_Time,status = tvdb_data
            #           series_title,mode,submode,url,TVDB_ID,IMDB_ID,TVDBbanner,TVDBposter,TVDBfanart,first_aired,date,year,actors,genres,network,plot,runtime,rating,Airs_DayOfWeek,Airs_Time,status,has_full_episodes,favor
            showdata = [series_title,mode,submode,url,TVDB_ID,IMDB_ID,TVDBbanner,TVDBposter,TVDBfanart,first_aired,date,year,actors,genres,network,plot,runtime,rating,Airs_DayOfWeek,Airs_Time,status,True,False,False]
        else:
            showdata = [series_title,mode,submode,url,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,True,False,False]
        c.execute('insert or replace into shows values (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)', showdata)
        conn.commit()
        return c.execute('select * from shows where series_title=? and mode=? and submode =?', (series_title,mode,submode)).fetchone()

def lookup_by_TVDBID_plot(tvdb_id):
    conn = sqlite.connect(db_file)
    conn.text_factory = str
    c = conn.cursor()
    showdata = c.execute('select * from shows where TVDB_ID =?', (tvdb_id,)).fetchone()
    prefixplot=''
    if showdata:
        series_title,mode,sitemode,url,TVDB_ID,IMDB_ID,TVDBbanner,TVDBposter,TVDBfanart,first_aired,date,year,actors,genres,network,plot,runtime,rating,Airs_DayOfWeek,Airs_Time,status,has_full_episodes,favor,hide = showdata
        if network<>None:
            prefixplot+='Station: %s' % network
            prefixplot+='\n'
        if Airs_DayOfWeek<>None and Airs_Time<>None:
            prefixplot+='Airs: %s @ %s' % (Airs_DayOfWeek,Airs_Time)
            prefixplot+='\n'
        if status<>None:
            prefixplot+='Status: %s' % status
            prefixplot+='\n'
        if prefixplot <> '':
            prefixplot+='\n'
        if plot<>None:
            prefixplot=prefixplot.encode('utf-8', 'ignore')+plot.decode("utf-8").encode('utf-8', 'ignore')
    return prefixplot
        
def refreshShow():
    series_title,mode,submode,url = args.url.split('<join>')
    lookup_db(series_title,mode,submode,url,forceRefresh=True)

def deleteShow():
    series_title,mode,submode,url = args.url.split('<join>')
    conn = sqlite.connect(db_file)
    conn.text_factory = str
    c = conn.cursor()
    c.execute('delete from shows where series_title=? and mode=? and submode =?', (series_title,mode,submode))
    conn.commit()
    c.close()

def favorShow():
    series_title,mode,submode,url = args.url.split('<join>')
    conn = sqlite.connect(db_file)
    conn.text_factory = str
    c = conn.cursor()
    c.execute("update shows set favor=? where series_title=? and mode=? and submode =?", (True,series_title,mode,submode))
    conn.commit()
    c.close()

def unfavorShow():
    series_title,mode,submode,url = args.url.split('<join>')
    conn = sqlite.connect(db_file)
    conn.text_factory = str
    c = conn.cursor()
    c.execute("update shows set favor=? where series_title=? and mode=? and submode =?", (False,series_title,mode,submode))
    conn.commit()
    c.close()

def hideShow():
    series_title,mode,submode,url = args.url.split('<join>')
    conn = sqlite.connect(db_file)
    conn.text_factory = str
    c = conn.cursor()
    c.execute("update shows set hide=? where series_title=? and mode=? and submode =?", (True,series_title,mode,submode))
    conn.commit()
    c.close()

def unhideShow():
    series_title,mode,submode,url = args.url.split('<join>')
    conn = sqlite.connect(db_file)
    conn.text_factory = str
    c = conn.cursor()
    c.execute("update shows set hide=? where series_title=? and mode=? and submode =?", (False,series_title,mode,submode))
    conn.commit()
    c.close()
    
def create_db():
    conn = sqlite.connect(db_file)
    conn.text_factory = str
    c = conn.cursor()
    c.execute('''CREATE TABLE shows(
                 series_title TEXT,
                 mode TEXT,
                 submode TEXT,
                 url TEXT,
                 TVDB_ID TEXT,
                 IMDB_ID TEXT,
                 TVDBbanner TEXT,
                 TVDBposter TEXT,
                 TVDBfanart TEXT,
                 first_aired TEXT,
                 date TEXT,
                 year INTEGER,
                 actors TEXT,
                 genres TEXT,
                 network TEXT,
                 plot TEXT,
                 runtime TEXT,
                 rating float,
                 Airs_DayOfWeek TEXT,
                 Airs_Time TEXT,
                 status TEXT,
                 has_full_episodes BOOLEAN,
                 favor BOOLEAN,
                 hide BOOLEAN,
                 PRIMARY KEY(series_title,mode,submode)
                 );''')
    conn.commit()
    c.close()

def refresh_db():
    dialog = xbmcgui.DialogProgress()
    dialog.create('Caching')
    total_stations = len(site_dict)
    current = 0
    increment = 100.0 / total_stations
    for network, name in site_dict.iteritems():
        if addoncompat.get_setting(network) == 'true':
            percent = int(increment*current)
            dialog.update(percent,'Scanning %s' % name,'Grabbing Show list')
            exec 'import %s' % network
            exec 'showdata = %s.masterlist()' % network
            total_shows = len(showdata)
            current_show = 0
            for show in showdata:
                percent = int((increment*current)+(float(current_show)/total_shows)*increment)
                dialog.update(percent,'Scanning %s' % name,'Looking up %s' % show[0] )
                lookup_db(show[0],show[1],show[2],show[3])
                current_show += 1
                if (dialog.iscanceled()):
                    return False
        current += 1
        
def formatDate(inputDate='',inputFormat='',outputFormat='%Y-%m-%d',epoch=False):
    if epoch:
        return time.strftime(outputFormat,time.localtime(epoch))
    else:
        return time.strftime(outputFormat,time.strptime(inputDate, inputFormat))

def setView(type='root'):
    confluence_views = [500,501,502,503,504,508]
    #types: files, songs, artists, albums, movies, tvshows, episodes, musicvideos
    if type == 'root':
        xbmcplugin.setContent(pluginhandle, 'movies')
    elif type == 'seasons':
        xbmcplugin.setContent(pluginhandle, 'movies')
    else:
        if type == 'tvshows':
            xbmcplugin.addSortMethod(pluginhandle, xbmcplugin.SORT_METHOD_LABEL)
            #xbmcplugin.addSortMethod(pluginhandle, xbmcplugin.SORT_METHOD_STUDIO)
            #xbmcplugin.addSortMethod(pluginhandle, xbmcplugin.SORT_METHOD_GENRE)
            #xbmcplugin.addSortMethod(pluginhandle, xbmcplugin.SORT_METHOD_DURATION)
            #xbmcplugin.addSortMethod(pluginhandle, xbmcplugin.SORT_METHOD_VIDEO_RATING)
            #xbmcplugin.addSortMethod(pluginhandle, xbmcplugin.SORT_METHOD_DATE)
        xbmcplugin.setContent(pluginhandle, type)
    viewenable=addoncompat.get_setting("viewenable")
    if viewenable == 'true':
        view=int(addoncompat.get_setting(type+'view'))
        xbmc.executebuiltin("Container.SetViewMode("+str(confluence_views[view])+")")  

def addVideo(u,displayname,thumb=False,fanart=False,infoLabels=False):
    if not fanart:
        if args.__dict__.has_key('fanart'): fanart = args.fanart
        else: fanart = plugin_fanart
    if not thumb:
        if args.__dict__.has_key('thumb'): thumb = args.thumb
        else: thumb = ''
    item=xbmcgui.ListItem(displayname, iconImage=thumb, thumbnailImage=thumb)
    item.setInfo( type="Video", infoLabels=infoLabels)
    item.setProperty('fanart_image',fanart)
    item.setProperty('IsPlayable', 'true')
    xbmcplugin.addDirectoryItem(pluginhandle,url=u,listitem=item,isFolder=False)

"""
    ADD DIRECTORY
"""

def addDirectory(name, mode='', sitemode='', url='', thumb=False, fanart=False, description=False, aired='', genre='',count=0):
    if not fanart:
        if args.__dict__.has_key('fanart'): fanart = args.fanart
        else: fanart = plugin_fanart
    if not thumb:
        if args.__dict__.has_key('poster'): thumb = args.poster
        elif args.__dict__.has_key('thumb'): thumb = args.thumb
        else: thumb = ''
    if args.__dict__.has_key('name'): showname = args.name
    else:showname=''
    if not description:
        if args.__dict__.has_key('tvdb_id'):
            description=lookup_by_TVDBID_plot(args.tvdb_id)
        elif site_descriptions.has_key(mode):
            description=site_descriptions[mode]
        else:
            description=''
    

    infoLabels={ "Title":name,
                 #"TVShowTitle":showname,
                 "Genre":genre,
                 "premiered":aired,
                 "Plot":description,
                 "count":count}
    
    u  = sys.argv[0]
    u += '?url="'+urllib.quote_plus(url)+'"'
    u += '&mode="'+mode+'"'
    u += '&sitemode="'+sitemode+'"'
    u += '&thumb="'+urllib.quote_plus(thumb)+'"'
    u += '&fanart="'+urllib.quote_plus(fanart)+'"'
    u += '&name="'+urllib.quote_plus(name)+'"'
    if args.__dict__.has_key('tvdb_id'):
        u += '&tvdb_id="'+urllib.quote_plus(args.tvdb_id)+'"'
    item=xbmcgui.ListItem(name, iconImage=thumb, thumbnailImage=thumb)
    item.setProperty('fanart_image',fanart)
    item.setInfo( type="Video", infoLabels=infoLabels)
    xbmcplugin.addDirectoryItem(handle=pluginhandle,url=u,listitem=item,isFolder=True)
    
def addShow(series_title, mode='', sitemode='', url='', thumb='', fanart='', TVDBposter=False, TVDB_ID=False, infoLabels=False, favor=False, hide=False):
    if not os.path.exists(db_file):
        create_db()
    if not infoLabels:
        infoLabels={}
        showdata = lookup_db(series_title,mode,sitemode,url)
        #series_title,mode,submode,url,TVDB_ID,IMDB_ID,TVDBbanner,TVDBposter,TVDBfanart,first_aired,date,year,actors,genres,network,plot,runtime,rating,Airs_DayOfWeek,Airs_Time,status,has_full_episodes,favor
        series_title,mode,sitemode,url,TVDB_ID,IMDB_ID,TVDBbanner,TVDBposter,TVDBfanart,first_aired,date,year,actors,genres,network,plot,runtime,rating,Airs_DayOfWeek,Airs_Time,status,has_full_episodes,favor,hide = showdata
        if TVDBfanart:
            fanart=TVDBfanart
        else:
            if args.__dict__.has_key('fanart'): fanart = args.fanart
            else: fanart=''
        if TVDBbanner:
            thumb=TVDBbanner
        elif TVDBposter:
            thumb=TVDBposter
        else:
            thumb=os.path.join(imagepath,mode+'.png')
        series_title = series_title.decode("utf-8")
        infoLabels['Title']=series_title.encode('utf-8', 'ignore')
        infoLabels['TVShowTitle']=series_title.encode('utf-8', 'ignore')
        prefixplot=''
        if network<>None:
            if site_dict[mode] <> network:
                prefixplot+='Network: %s' % network
                prefixplot+='\n'
                prefixplot+='Station: %s' % site_dict[mode]
                prefixplot+='\n'
            else:
                prefixplot+='Station: %s' % site_dict[mode]
                prefixplot+='\n'
        else:
            prefixplot+='Station: %s' % site_dict[mode]
            prefixplot+='\n'      
        if Airs_DayOfWeek<>None and Airs_Time<>None:
            prefixplot+='Airs: %s @ %s' % (Airs_DayOfWeek,Airs_Time)
            prefixplot+='\n'
        if status<>None:
            prefixplot+='Status: %s' % status
            prefixplot+='\n'
        if prefixplot <> '':
            prefixplot+='\n'
        if plot<>None:
            infoLabels['Plot']=prefixplot.encode('utf-8', 'ignore')+plot.decode("utf-8").encode('utf-8', 'ignore')
        else:
            infoLabels['Plot']=prefixplot
        if date: infoLabels['date']=date
        if first_aired<>None: infoLabels['aired']=first_aired
        if year<>None: infoLabels['Year']=year
        if actors<>None:
            actors = actors.decode("utf-8").encode('utf-8', 'ignore').strip('|').split('|')
            if actors[0] <> '':
                infoLabels['cast']=actors
        if genres<>None: infoLabels['genre']=genres.encode('utf-8', 'ignore').replace('|',',').strip(',')
        if network<>None: infoLabels['studio']=network.encode('utf-8', 'ignore')
        if runtime<>None: infoLabels['duration']=runtime
        if rating<>None: infoLabels['rating']=rating
    name = series_title
    series_title = series_title.replace(u'\xae','%A9').replace(u'\xe9','%E9').replace(u'\u2122','%99').replace(u'\u2122','%99').replace(u'\u2019','')
    u  = sys.argv[0]
    u += '?url="'+urllib.quote_plus(url)+'"'
    u += '&mode="'+mode+'"'
    u += '&sitemode="'+sitemode+'"'
    u += '&thumb="'+urllib.quote_plus(thumb)+'"'
    if TVDB_ID:
        u += '&tvdb_id="'+urllib.quote_plus(TVDB_ID)+'"'
    if plugin_fanart <> fanart:
        u += '&fanart="'+urllib.quote_plus(fanart)+'"'
    if TVDBposter:
        u += '&poster="'+urllib.quote_plus(TVDBposter)+'"'
    u += '&name="'+urllib.quote_plus(series_title)+'"'
    
    cm=[]
    if favor:
        fav_u=sys.argv[0]+"?url=\""+urllib.quote_plus('<join>'.join([series_title,mode,sitemode,url]))+"\"&mode='common'"+"&sitemode='unfavorShow'"
        cm.append( ('Remove Favorite %s' % name, "XBMC.RunPlugin(%s)" % fav_u) )
    else:
        fav_u=sys.argv[0]+"?url=\""+urllib.quote_plus('<join>'.join([series_title,mode,sitemode,url]))+"\"&mode='common'"+"&sitemode='favorShow'"
        cm.append( ('Favorite %s' % name, "XBMC.RunPlugin(%s)" % fav_u) )
    refresh_u=sys.argv[0]+"?url=\""+urllib.quote_plus('<join>'.join([series_title,mode,sitemode,url]))+"\"&mode='common'"+"&sitemode='refreshShow'"
    cm.append( ('Refresh TVDB Data', "XBMC.RunPlugin(%s)" % refresh_u) )
    if hide:
        hide_u=sys.argv[0]+"?url=\""+urllib.quote_plus('<join>'.join([series_title,mode,sitemode,url]))+"\"&mode='common'"+"&sitemode='unhideShow'"
        cm.append( ('UnHide Show', "XBMC.RunPlugin(%s)" % hide_u) )
    else:  
        hide_u=sys.argv[0]+"?url=\""+urllib.quote_plus('<join>'.join([series_title,mode,sitemode,url]))+"\"&mode='common'"+"&sitemode='hideShow'"
        cm.append( ('Hide Show', "XBMC.RunPlugin(%s)" % hide_u) )
    delete_u=sys.argv[0]+"?url=\""+urllib.quote_plus('<join>'.join([series_title,mode,sitemode,url]))+"\"&mode='common'"+"&sitemode='deleteShow'"
    cm.append( ('Delete Show', "XBMC.RunPlugin(%s)" % delete_u) )

    item=xbmcgui.ListItem(name, iconImage=thumb, thumbnailImage=thumb)
    item.addContextMenuItems( cm )
    item.setProperty('fanart_image',fanart)
    item.setInfo( type="Video", infoLabels=infoLabels)
    xbmcplugin.addDirectoryItem(handle=pluginhandle,url=u,listitem=item,isFolder=True)

def getURL( url , values = None ,proxy = False, referer=False):
    try:
        if proxy == True:
            us_proxy = 'http://' + addoncompat.get_setting('us_proxy') + ':' + addoncompat.get_setting('us_proxy_port')
            proxy_handler = urllib2.ProxyHandler({'http':us_proxy})
            if addoncompat.get_setting('us_proxy_pass') <> '' and addoncompat.get_setting('us_proxy_user') <> '':
                print 'Using authenticated proxy: ' + us_proxy
                password_mgr = urllib2.HTTPPasswordMgrWithDefaultRealm()
                password_mgr.add_password(None, us_proxy, addoncompat.get_setting('us_proxy_user'), addoncompat.get_setting('us_proxy_pass'))
                proxy_auth_handler = urllib2.ProxyBasicAuthHandler(password_mgr)
                opener = urllib2.build_opener(proxy_handler, proxy_auth_handler)
            else:
                print 'Using proxy: ' + us_proxy
                opener = urllib2.build_opener(proxy_handler)
            urllib2.install_opener(opener)

        print 'FREE CABLE --> common :: getURL :: url = '+url
        if values == None:
            req = urllib2.Request(url)
        else:
            data = urllib.urlencode(values)
            req = urllib2.Request(url,data)
        if referer:
            req.add_header('Referer', referer)
        req.add_header('User-Agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.7; rv:13.0) Gecko/20100101 Firefox/13.0.1')
        response = urllib2.urlopen(req)
        link=response.read()
        response.close()
    except urllib2.HTTPError, error:
        print 'Error reason: ', error
        return error.read()
    else:
        return link
    
def getRedirect( url , values = None ,proxy = False, referer=False):
    try:
        if proxy == True:
            us_proxy = 'http://' + addoncompat.get_setting('us_proxy') + ':' + addoncompat.get_setting('us_proxy_port')
            proxy_handler = urllib2.ProxyHandler({'http':us_proxy})
            if addoncompat.get_setting('us_proxy_pass') <> '' and addoncompat.get_setting('us_proxy_user') <> '':
                print 'Using authenticated proxy: ' + us_proxy
                password_mgr = urllib2.HTTPPasswordMgrWithDefaultRealm()
                password_mgr.add_password(None, us_proxy, addoncompat.get_setting('us_proxy_user'), addoncompat.get_setting('us_proxy_pass'))
                proxy_auth_handler = urllib2.ProxyBasicAuthHandler(password_mgr)
                opener = urllib2.build_opener(proxy_handler, proxy_auth_handler)
            else:
                print 'Using proxy: ' + us_proxy
                opener = urllib2.build_opener(proxy_handler)
            urllib2.install_opener(opener)

        print 'FREE CABLE --> common :: getRedirect :: url = '+url
        if values == None:
            req = urllib2.Request(url)
        else:
            data = urllib.urlencode(values)
            req = urllib2.Request(url,data)
        if referer:
            req.add_header('Referer', referer)
        req.add_header('User-Agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.7; rv:13.0) Gecko/20100101 Firefox/13.0.1')
        response = urllib2.urlopen(req)
        finalurl=response.geturl()
        response.close()
    except urllib2.HTTPError, error:
        print 'Error reason: ', error
        return error.read()
    else:
        return finalurl

