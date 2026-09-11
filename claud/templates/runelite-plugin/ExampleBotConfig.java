package com.example.bot;

import net.runelite.api.coords.WorldPoint;
import net.runelite.client.config.Config;
import net.runelite.client.config.ConfigGroup;
import net.runelite.client.config.ConfigItem;

@ConfigGroup("examplebot")
public interface ExampleBotConfig extends Config
{
	@ConfigItem(keyName = "enabled", name = "Enabled", description = "Run the bot loop")
	default boolean enabled() { return false; }

	// Lumbridge trees / bank as placeholders; replace with tiles on your server
	default WorldPoint treeTile() { return new WorldPoint(3190, 3240, 0); }
	default WorldPoint bankTile() { return new WorldPoint(3208, 3220, 2); }
}
