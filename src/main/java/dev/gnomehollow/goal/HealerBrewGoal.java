package dev.gnomehollow.goal;

import dev.gnomehollow.entity.GnomeEntity;
import java.util.Optional;
import net.minecraft.core.particles.ParticleTypes;
import dev.gnomehollow.ModSounds;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraft.world.item.alchemy.PotionContents;
import net.minecraft.world.item.alchemy.Potions;
import net.minecraft.world.level.block.Blocks;

/** Healer: loopt naar een brewing stand, brouwt (bubbels, geluid) en legt af en toe een drankje in een kist/vat. */
public class HealerBrewGoal extends WorkGoal {
	public HealerBrewGoal(GnomeEntity gnome) {
		super(gnome);
	}

	@Override
	protected boolean findTarget(ServerLevel level) {
		Optional<net.minecraft.core.BlockPos> stand = GnomeUtil.findNearest(level, this.gnome.blockPosition(), 16, 3,
				s -> s.is(Blocks.BREWING_STAND));
		if (stand.isEmpty()) return false;
		this.target = stand.get();
		Optional<net.minecraft.core.BlockPos> spot = GnomeUtil.findStandNear(level, this.target);
		if (spot.isEmpty()) return false;
		this.stand = spot.get();
		return true;
	}

	@Override
	protected boolean targetStillValid(ServerLevel level) {
		return level.getBlockState(this.target).is(Blocks.BREWING_STAND);
	}

	@Override
	protected SoundEvent workSound() {
		return ModSounds.WORK_BREW;
	}

	@Override
	protected int duration() {
		return 240;
	}

	@Override
	protected String animation() {
		return "work";
	}

	@Override
	protected double reach() {
		return 2.6;
	}

	@Override
	protected void work(ServerLevel level, int t) {
		if (t % 8 == 0) {
			level.sendParticles(ParticleTypes.WITCH, this.target.getX() + 0.5, this.target.getY() + 0.9,
					this.target.getZ() + 0.5, 2, 0.15, 0.1, 0.15, 0.0);
			level.sendParticles(ParticleTypes.BUBBLE_POP, this.target.getX() + 0.5, this.target.getY() + 0.7,
					this.target.getZ() + 0.5, 2, 0.15, 0.1, 0.15, 0.0);
		}
		if (t % 50 == 0) {
			level.playSound(null, this.target, SoundEvents.BREWING_STAND_BREW, SoundSource.NEUTRAL, 0.7F, 1.0F);
		}
	}

	@Override
	protected void finish(ServerLevel level, boolean completed) {
		if (!completed || this.gnome.getRandom().nextInt(100) >= 35) return;
		ItemStack potion = PotionContents.createItemStack(Items.POTION,
				this.gnome.getRandom().nextBoolean() ? Potions.HEALING : Potions.REGENERATION);
		if (!GnomeUtil.insertIntoNearbyContainer(level, this.target, 8, potion)) {
			this.gnome.spawnAtLocation(level, potion);
		}
	}
}
