import logging

import svgwrite

from src.renderers.base_renderer import BaseRenderer

logger = logging.getLogger(__name__)


class ProfileCardRenderer(BaseRenderer):
    def _create_drawing(self, user_data, contribution_data=None):
        if not user_data:
            logger.warning("No user data for profile card")
            return None

        card_width = 800
        card_height = 200
        padding = 24

        dwg = svgwrite.Drawing(
            size=(f"{card_width}px", f"{card_height}px"),
        )

        bg_color = self._get_color("card_bg")
        text_color = self._get_color("text")
        text_secondary = self._get_color("text_secondary")
        accent = self._get_color("accent")
        border_color = self._get_color("border")

        dwg.add(dwg.rect(
            insert=(0, 0),
            size=(card_width, card_height),
            rx=self.card_radius,
            fill=bg_color,
            stroke=border_color,
            stroke_width=1,
        ))

        avatar_size = 80
        avatar_x = padding
        avatar_y = padding
        avatar_url = user_data.get("avatar_url", "")

        if avatar_url:
            clip_path = dwg.defs.add(dwg.clipPath(id="avatar-clip"))
            clip_path.add(dwg.circle(
                center=(avatar_x + avatar_size / 2, avatar_y + avatar_size / 2),
                r=avatar_size / 2,
            ))
            dwg.add(dwg.image(
                href=avatar_url,
                insert=(avatar_x, avatar_y),
                size=(avatar_size, avatar_size),
                clip_path="url(#avatar-clip)",
            ))
        else:
            dwg.add(dwg.circle(
                center=(avatar_x + avatar_size / 2, avatar_y + avatar_size / 2),
                r=avatar_size / 2,
                fill=accent,
            ))

        text_x = avatar_x + avatar_size + 20
        name = user_data.get("name", "") or user_data.get("login", "")
        login = user_data.get("login", "")

        dwg.add(dwg.text(
            name,
            insert=(text_x, avatar_y + 22),
            fill=text_color,
            font_size="20px",
            font_family=self.font_family,
            font_weight="bold",
        ))

        if login and login != name:
            dwg.add(dwg.text(
                f"@{login}",
                insert=(text_x, avatar_y + 42),
                fill=accent,
                font_size="13px",
                font_family=self.font_family,
            ))

        bio = user_data.get("bio", "")
        if bio:
            max_chars = 80
            display_bio = bio[:max_chars] + "..." if len(bio) > max_chars else bio
            dwg.add(dwg.text(
                display_bio,
                insert=(text_x, avatar_y + 62),
                fill=text_secondary,
                font_size="12px",
                font_family=self.font_family,
            ))

        stats_y = avatar_y + avatar_size + 20
        stats = [
            ("Repos", user_data.get("public_repos", 0)),
            ("Stars", user_data.get("total_stars", 0)),
            ("Followers", user_data.get("followers", 0)),
            ("Following", user_data.get("following", 0)),
        ]

        if contribution_data:
            streak = contribution_data.get("streak", {})
            stats.append(("Longest Streak", streak.get("longest", 0)))
            stats.append(("Current Streak", streak.get("current", 0)))

        account_age = user_data.get("account_age_years", 0)
        if account_age:
            stats.append(("Account Age", f"{account_age}y"))

        stat_width = (card_width - 2 * padding) / len(stats)
        for i, (label, value) in enumerate(stats):
            sx = padding + i * stat_width + stat_width / 2

            dwg.add(dwg.text(
                str(value),
                insert=(sx, stats_y + 10),
                fill=text_color,
                font_size="18px",
                font_family=self.font_family,
                font_weight="bold",
                text_anchor="middle",
            ))

            dwg.add(dwg.text(
                label,
                insert=(sx, stats_y + 28),
                fill=text_secondary,
                font_size="10px",
                font_family=self.font_family,
                text_anchor="middle",
            ))

        return dwg

    def render(self, user_data, contribution_data=None):
        dwg = self._create_drawing(user_data, contribution_data)
        if not dwg:
            return None

        filepath = self._get_filepath("profile-card.svg")
        dwg.filename = str(filepath)
        dwg.save()
        logger.info(f"Profile card saved to {filepath}")
        return str(filepath)

    def _render_to_string(self, user_data, contribution_data=None):
        dwg = self._create_drawing(user_data, contribution_data)
        if not dwg:
            return ""
        return dwg.tostring()
