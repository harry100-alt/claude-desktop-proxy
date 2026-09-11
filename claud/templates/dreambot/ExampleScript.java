import org.dreambot.api.methods.container.impl.Inventory;
import org.dreambot.api.methods.container.impl.bank.Bank;
import org.dreambot.api.methods.interactive.GameObjects;
import org.dreambot.api.methods.interactive.Players;
import org.dreambot.api.methods.map.Area;
import org.dreambot.api.methods.walking.impl.Walking;
import org.dreambot.api.script.AbstractScript;
import org.dreambot.api.script.Category;
import org.dreambot.api.script.ScriptManifest;
import org.dreambot.api.utilities.Sleep;
import org.dreambot.api.wrappers.interactive.GameObject;

/**
 * DreamBot script skeleton (DreamBot 3 API). Compile against DreamBot's client.jar
 * (~/DreamBot/BotData/client.jar) and drop the .class/.jar into ~/DreamBot/Scripts/.
 *
 * DreamBot targets the official game; it will only work on a private server if that server is
 * built to accept the DreamBot client, which is rare. Included as a reference for API shape.
 */
@ScriptManifest(name = "Example Chopper", description = "Chop and bank", author = "you", version = 1.0, category = Category.WOODCUTTING)
public class ExampleScript extends AbstractScript
{
	private final Area TREES = new Area(3185, 3245, 3195, 3235);
	private final Area BANK = new Area(3207, 3222, 3210, 3216, 2);

	@Override
	public int onLoop()
	{
		if (Inventory.isFull())
		{
			if (!BANK.contains(Players.getLocal())) { Walking.walk(BANK.getRandomTile()); return Sleep.random(600, 1200); }
			if (!Bank.isOpen()) { Bank.open(); Sleep.sleepUntil(Bank::isOpen, 4000); return 200; }
			Bank.depositAllItems();
			return Sleep.random(400, 800);
		}
		if (!TREES.contains(Players.getLocal())) { Walking.walk(TREES.getRandomTile()); return Sleep.random(600, 1200); }
		if (Players.getLocal().isAnimating()) return 300;
		GameObject tree = GameObjects.closest(o -> o != null && "Tree".equals(o.getName()) && o.hasAction("Chop down") && TREES.contains(o));
		if (tree != null && tree.interact("Chop down"))
		{
			Sleep.sleepUntil(() -> Players.getLocal().isAnimating(), 3000);
		}
		return Sleep.random(300, 700);
	}
}
