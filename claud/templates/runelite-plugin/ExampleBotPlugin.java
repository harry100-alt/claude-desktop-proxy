package com.example.bot;

import com.google.inject.Provides;
import javax.inject.Inject;
import net.runelite.api.Client;
import net.runelite.api.GameObject;
import net.runelite.api.GameState;
import net.runelite.api.ItemContainer;
import net.runelite.api.MenuAction;
import net.runelite.api.NPC;
import net.runelite.api.Player;
import net.runelite.api.Skill;
import net.runelite.api.coords.WorldPoint;
import net.runelite.api.events.GameTick;
import net.runelite.api.gameval.InterfaceID;
import net.runelite.api.gameval.InventoryID;
import net.runelite.api.gameval.ItemID;
import net.runelite.api.gameval.ObjectID;
import net.runelite.api.widgets.Widget;
import net.runelite.client.config.ConfigManager;
import net.runelite.client.eventbus.Subscribe;
import net.runelite.client.plugins.Plugin;
import net.runelite.client.plugins.PluginDescriptor;

/**
 * Skeleton for an automation plugin on a RuneLite-based client (many private servers ship one).
 *
 * The pattern is a tick-driven state machine: every GameTick (600 ms) look at the world, decide the
 * next state, and issue at most ONE action. Never sleep on the client thread.
 *
 * Interaction: stock RuneLite has no "click this NPC" API. Automation forks (Microbot, EthanVann's
 * packet utils, Devious, etc.) add one. The two common approaches are shown in `interact()`:
 *   1. client.menuAction(...) - invokes a menu entry directly (works on most RuneLite forks).
 *   2. a mouse/packet helper from the fork you are on.
 *
 * Replace ObjectID/ItemID constants with ones from ../data/*.csv for your server's revision.
 */
@PluginDescriptor(name = "Example Bot", description = "Tick-based state machine skeleton", enabledByDefault = false)
public class ExampleBotPlugin extends Plugin
{
	private enum State { IDLE, WALK_TO_TREE, CHOP, WALK_TO_BANK, BANK, STOP }

	@Inject private Client client;
	@Inject private ExampleBotConfig config;

	private State state = State.IDLE;
	private int lastActionTick = 0;
	private int idleTicks = 0;

	@Provides
	ExampleBotConfig provideConfig(ConfigManager cm) { return cm.getConfig(ExampleBotConfig.class); }

	@Override protected void startUp() { state = State.IDLE; }
	@Override protected void shutDown() { state = State.STOP; }

	@Subscribe
	public void onGameTick(GameTick e)
	{
		if (client.getGameState() != GameState.LOGGED_IN || !config.enabled()) return;
		Player me = client.getLocalPlayer();
		if (me == null) return;

		// simple reaction-delay: don't act every tick
		if (client.getTickCount() - lastActionTick < 1 + (int) (Math.random() * 2)) return;

		boolean animating = me.getAnimation() != -1;
		boolean moving = me.getPoseAnimation() != me.getIdlePoseAnimation();
		idleTicks = (animating || moving) ? 0 : idleTicks + 1;

		switch (state)
		{
			case IDLE:
				state = inventoryFull() ? State.WALK_TO_BANK : State.WALK_TO_TREE;
				break;

			case WALK_TO_TREE:
			case CHOP:
				if (inventoryFull()) { state = State.WALK_TO_BANK; break; }
				if (idleTicks < 2) break;                  // still chopping / walking
				GameObject tree = nearestObject(ObjectID.TREE, 15);
				if (tree == null) { state = State.WALK_TO_TREE; walkTo(config.treeTile()); break; }
				interactObject(tree, "Chop down", MenuAction.GAME_OBJECT_FIRST_OPTION);
				state = State.CHOP;
				break;

			case WALK_TO_BANK:
			case BANK:
				if (isBankOpen()) { depositAll(); state = State.IDLE; break; }
				GameObject booth = nearestObject(ObjectID.BANKBOOTH, 15);
				if (booth == null) { walkTo(config.bankTile()); break; }
				interactObject(booth, "Bank", MenuAction.GAME_OBJECT_FIRST_OPTION);
				state = State.BANK;
				break;

			case STOP:
			default:
				break;
		}
	}

	// ---------- world queries ----------

	private boolean inventoryFull()
	{
		ItemContainer inv = client.getItemContainer(InventoryID.INV);
		return inv != null && inv.count() >= 28;
	}

	private boolean isBankOpen()
	{
		Widget w = client.getWidget(InterfaceID.BANKMAIN, 0);
		return w != null && !w.isHidden();
	}

	private GameObject nearestObject(int id, int maxDist)
	{
		WorldPoint me = client.getLocalPlayer().getWorldLocation();
		GameObject best = null;
		int bestD = Integer.MAX_VALUE;
		for (var tile : client.getTopLevelWorldView().getScene().getTiles()[client.getTopLevelWorldView().getPlane()])
		{
			if (tile == null) continue;
			for (var t : tile)
			{
				if (t == null) continue;
				for (GameObject go : t.getGameObjects())
				{
					if (go == null || go.getId() != id) continue;
					int d = go.getWorldLocation().distanceTo(me);
					if (d < bestD && d <= maxDist) { best = go; bestD = d; }
				}
			}
		}
		return best;
	}

	private NPC nearestNpc(int id)
	{
		WorldPoint me = client.getLocalPlayer().getWorldLocation();
		NPC best = null; int bestD = Integer.MAX_VALUE;
		for (NPC n : client.getNpcs())
		{
			if (n.getId() != id) continue;
			int d = n.getWorldLocation().distanceTo(me);
			if (d < bestD) { best = n; bestD = d; }
		}
		return best;
	}

	// ---------- actions (one per tick) ----------

	private void interactObject(GameObject go, String option, MenuAction action)
	{
		// p0/p1 are the scene x/y of the object for GAME_OBJECT_* actions; id is the object id.
		var lp = go.getLocalLocation();
		client.menuAction(lp.getSceneX(), lp.getSceneY(), action, go.getId(), -1, option, "");
		lastActionTick = client.getTickCount();
	}

	private void interactNpc(NPC npc, String option, MenuAction action)
	{
		// for NPC_* actions the id argument is the npc INDEX, not the npc id.
		client.menuAction(0, 0, action, npc.getIndex(), -1, option, "");
		lastActionTick = client.getTickCount();
	}

	private void walkTo(WorldPoint wp)
	{
		// Stock RuneLite: convert to scene coords and issue a WALK menu action.
		var lp = net.runelite.api.coords.LocalPoint.fromWorld(client.getTopLevelWorldView(), wp);
		if (lp == null) return; // not in the loaded scene: use a web-walker from your fork instead
		client.menuAction(lp.getSceneX(), lp.getSceneY(), MenuAction.WALK, 0, -1, "Walk here", "");
		lastActionTick = client.getTickCount();
	}

	private void depositAll()
	{
		// Bankmain "Deposit inventory" button: InterfaceID.Bankmain.DEPOSITINV (see data/interface_children.csv)
		client.menuAction(-1, InterfaceID.Bankmain.DEPOSITINV, MenuAction.CC_OP, 1, -1, "Deposit inventory", "");
		lastActionTick = client.getTickCount();
	}
}
