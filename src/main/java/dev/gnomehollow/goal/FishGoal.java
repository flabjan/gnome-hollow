package dev.gnomehollow.goal;

import dev.gnomehollow.entity.GnomeEntity;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.core.particles.ParticleTypes;
import dev.gnomehollow.ModSounds;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.tags.FluidTags;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;

/** Fisherman: zoekt open water vlakbij, gaat aan de oever staan en vist. De vangst gaat in een vat (barrel) in de buurt. */
public class FishGoal extends WorkGoal {
	public FishGoal(GnomeEntity gnome) {
		super(gnome);
	}

	@Override
	protected boolean findTarget(ServerLevel level) {
		BlockPos origin = this.gnome.blockPosition();
		for (int i = 0; i < 80; i++) {
			BlockPos w = origin.offset(this.gnome.getRandom().nextInt(29) - 14, this.gnome.getRandom().nextInt(7) - 3,
					this.gnome.getRandom().nextInt(29) - 14);
			var fluid = level.getFluidState(w);
			if (!fluid.is(FluidTags.WATER) || !fluid.isSource()) continue;
			if (!level.getBlockState(w.above()).isAir()) continue;
			for (Direction d : Direction.Plane.HORIZONTAL) {
				for (int up = 0; up <= 1; up++) {
					BlockPos s = w.relative(d).above(up);
					if (GnomeUtil.isStandable(level, s)) {
						this.target = w;
						this.stand = s;
						return true;
					}
				}
			}
		}
		return false;
	}

	@Override
	protected SoundEvent workSound() {
		return ModSounds.WORK_FISH;
	}

	@Override
	protected boolean celebrates() {
		return false;
	}

	@Override
	protected int duration() {
		return 240;
	}

	@Override
	protected String animation() {
		return "fish";
	}

	@Override
	protected double reach() {
		return 3.5;
	}

	@Override
	protected int nextCooldown() {
		return 100 + this.gnome.getRandom().nextInt(200);
	}

	@Override
	protected void work(ServerLevel level, int t) {
		if (t % 25 == 0) {
			level.sendParticles(ParticleTypes.FISHING, this.target.getX() + 0.5, this.target.getY() + 1.0,
					this.target.getZ() + 0.5, 4, 0.2, 0.0, 0.2, 0.0);
		}
		if (t == 90 || t == 170) {
			level.playSound(null, this.target, SoundEvents.FISHING_BOBBER_SPLASH, SoundSource.NEUTRAL, 0.4F, 1.2F);
		}
	}

	@Override
	protected void finish(ServerLevel level, boolean completed) {
		if (!completed) return;
		if (this.gnome.getRandom().nextInt(100) >= 70) {
			this.gnome.voice(ModSounds.NO, 0.6F);   // niks gevangen: "aww"
			return;
		}
		this.gnome.voice(ModSounds.FISH_CATCH, 1.0F);
		int r = this.gnome.getRandom().nextInt(100);
		ItemStack catchStack = new ItemStack(r < 55 ? Items.COD : r < 85 ? Items.SALMON : r < 95 ? Items.TROPICAL_FISH : Items.PUFFERFISH);
		if (!GnomeUtil.insertIntoNearbyContainer(level, this.gnome.blockPosition(), 24, catchStack)) {
			this.gnome.spawnAtLocation(level, catchStack);
		}
		level.playSound(null, this.gnome.blockPosition(), SoundEvents.ITEM_PICKUP, SoundSource.NEUTRAL, 0.5F, 1.0F);
	}
}
