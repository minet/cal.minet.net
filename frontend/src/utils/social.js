import discordIcon from '../assets/social/discord.svg'
import facebookIcon from '../assets/social/facebook.svg'
import githubIcon from '../assets/social/github.svg'
import linkedinIcon from '../assets/social/linkedin.svg'
import messengerIcon from '../assets/social/messenger.svg'
import minetIcon from '../assets/social/minet.svg'
import redditIcon from '../assets/social/reddit.svg'
import twitchIcon from '../assets/social/twitch.svg'
import whatsappIcon from '../assets/social/whatsapp.svg'
import youtubeIcon from '../assets/social/youtube.svg'
import blueskyIcon from '../assets/social/bluesky.svg'
import instagramIcon from '../assets/social/instagram.svg'

export function getSocialIcon(url) {
  if (!url) return null;
  const lowerUrl = url.toLowerCase();

  if (lowerUrl.includes('discord.') || lowerUrl.includes('discordapp.')) return discordIcon;
  if (lowerUrl.includes('facebook.com') || lowerUrl.includes('fb.com')) return facebookIcon;
  if (lowerUrl.includes('github.com')) return githubIcon;
  if (lowerUrl.includes('linkedin.com')) return linkedinIcon;
  if (lowerUrl.includes('messenger.com') || lowerUrl.includes('m.me')) return messengerIcon;
  if (lowerUrl.includes('reddit.com')) return redditIcon;
  if (lowerUrl.includes('twitch.tv')) return twitchIcon;
  if (lowerUrl.includes('whatsapp.com') || lowerUrl.includes('wa.me')) return whatsappIcon;
  if (lowerUrl.includes('youtube.com') || lowerUrl.includes('youtu.be')) return youtubeIcon;
  if (lowerUrl.includes('bsky.app')) return blueskyIcon;
  if (lowerUrl.includes('instagram.com')) return instagramIcon;
  if (lowerUrl.includes('minet.net')) return minetIcon;

  return null;
}
