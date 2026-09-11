import org.osbot.rs07.api.model.RS2Object;
import org.osbot.rs07.script.Script;
import org.osbot.rs07.script.ScriptManifest;
import org.osbot.rs07.utility.ConditionalSleep;

/**
 * OSBot script skeleton. Compile against osbot.jar, place the .jar in ~/OSBot/Scripts.
 * Same caveat as DreamBot: built for the official game client.
 */
@ScriptManifest(name = "Example Chopper", author = "you", version = 1.0, info = "Chop and bank", logo = "")
public class ExampleScript extends Script
{
	@Override
	public int onLoop() throws InterruptedException
	{
		if (getInventory().isFull())
		{
			if (!getBank().isOpen()) { getBank().open(); return 600; }
			getBank().depositAll();
			return 600;
		}
		if (myPlayer().isAnimating()) return 300;
		RS2Object tree = getObjects().closest(o -> "Tree".equals(o.getName()) && o.hasAction("Chop down"));
		if (tree != null && tree.interact("Chop down"))
		{
			new ConditionalSleep(3000) { @Override public boolean condition() { return myPlayer().isAnimating(); } }.sleep();
		}
		return random(300, 700);
	}
}
