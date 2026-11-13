package dev.gnomehollow.goal;

import dev.gnomehollow.entity.GnomeEntity;
import java.util.Optional;
import net.minecraft.core.BlockPos;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.Container;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.block.Blocks;

/** Builder: haalt bouwmaterialen uit de opslag (vat of kist) bij het eigen huis voordat hij gaat bouwen of repareren. */
public class CollectMaterialsGoal extends WorkGoal {
	public CollectMaterialsGoal(GnomeEntity gnome) {
		super(gnome);
	}

	@Override
	protected boolean findTarget(ServerLevel level) {
		if (this.gnome.materials() >= 3 || !this.gnome.hasHome()) return false;
		Optional<BlockPos> store = GnomeUtil.findNearest(level, this.gnome.home(), 12, 3, s -> s.is(Blocks.BARREL) || s.is(Blocks.CHEST));
		if (store.isEmpty()) return false;
		this.target = store.get();
		this.stand = GnomeUtil.findStandNear(level, this.target).orElse(this.target);
		return true;
	}

	@Override
	protected int duration() {
		return 90;
	}

	@Override
	protected String animation() {
		return "work";
	}

	@Override
	protected boolean celebrates() {
		return false;
	}

	@Override
	protected int nextCooldown() {
		return 40 + this.gnome.getRandom().nextInt(80);
	}

	@Override
	protected void work(ServerLevel level, int t) {
		if (t != 40) return;
		int gained = 3;   // ook zonder voorraad kan hij wat restmateriaal verzamelen
		if (level.getBlockEntity(this.target) instanceof Container c) {
			for (int i = 0; i < c.getContainerSize(); i++) {
				if (!c.getItem(i).isEmpty()) {
					ItemStack taken = c.removeItem(i, 1);
					if (!taken.isEmpty()) gained = 6;
					break;
				}
			}
		}
		this.gnome.addMaterials(gained);
		level.playSound(null, this.target, SoundEvents.ITEM_PICKUP, SoundSource.NEUTRAL, 0.5F, 1.0F);
	}
}
