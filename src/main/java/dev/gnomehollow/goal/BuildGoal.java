package dev.gnomehollow.goal;

import dev.gnomehollow.entity.GnomeEntity;
import net.minecraft.core.BlockPos;
import dev.gnomehollow.ModSounds;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.level.block.Blocks;

/** Builder: timmert rond het dorp kleine lantaarnpalen (2 hekjes + lantaarn). Maximaal 8 per gnome. */
public class BuildGoal extends WorkGoal {
	private static final int MAX_BUILT = 8;

	public BuildGoal(GnomeEntity gnome) {
		super(gnome);
	}

	@Override
	protected boolean findTarget(ServerLevel level) {
		if (this.gnome.builtCount() >= MAX_BUILT) return false;
		BlockPos home = this.gnome.home() != null ? this.gnome.home() : this.gnome.blockPosition();
		for (int i = 0; i < 50; i++) {
			int dx = this.gnome.getRandom().nextInt(21) - 10;
			int dz = this.gnome.getRandom().nextInt(21) - 10;
			if (Math.abs(dx) < 4 && Math.abs(dz) < 4) continue;
			for (int dy = 3; dy >= -3; dy--) {
				BlockPos p = home.offset(dx, dy, dz);
				boolean free = level.getBlockState(p).isAir() && level.getBlockState(p.above()).isAir()
						&& level.getBlockState(p.above(2)).isAir();
				boolean ground = level.getBlockState(p.below()).isFaceSturdy(level, p.below(), net.minecraft.core.Direction.UP)
						&& !level.getBlockState(p.below()).is(Blocks.DIRT_PATH);
				if (free && ground) {
					var spot = GnomeUtil.findStandNear(level, p);
					if (spot.isEmpty()) return false;
					this.target = p;
					this.stand = spot.get();
					return true;
				}
			}
		}
		return false;
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
	protected int nextCooldown() {
		return 500 + this.gnome.getRandom().nextInt(600);
	}

	private void place(ServerLevel level, BlockPos pos, net.minecraft.world.level.block.state.BlockState state) {
		if (level.getBlockState(pos).isAir()) {
			level.setBlock(pos, state, 3);
		}
		level.playSound(null, pos, SoundEvents.ANVIL_USE, SoundSource.NEUTRAL, 0.4F, 1.4F);
		this.gnome.voice(ModSounds.WORK_BUILD, 0.8F);
	}

	@Override
	protected void work(ServerLevel level, int t) {
		if (t == 20) this.place(level, this.target, Blocks.SPRUCE_FENCE.defaultBlockState());
		if (t == 45) this.place(level, this.target.above(), Blocks.SPRUCE_FENCE.defaultBlockState());
		if (t == 70) this.place(level, this.target.above(2), Blocks.LANTERN.defaultBlockState());
	}

	@Override
	protected void finish(ServerLevel level, boolean completed) {
		if (completed) this.gnome.addBuilt();
	}
}
