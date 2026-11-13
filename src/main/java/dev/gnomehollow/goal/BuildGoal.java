package dev.gnomehollow.goal;

import dev.gnomehollow.ModBlocks;
import dev.gnomehollow.ModSounds;
import dev.gnomehollow.entity.GnomeEntity;
import dev.gnomehollow.village.VillageInfo;
import net.minecraft.core.BlockPos;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.level.block.Blocks;

/**
 * Builder: onderhoudt het dorp (ontbrekende lampen op lantaarnpalen herstellen) en timmert kleine dingen bij
 * (bankje, bloemen, paddenstoeltje). Kost materialen die eerst verzameld moeten worden. Maximaal 10 nieuwe dingen per gnome.
 */
public class BuildGoal extends WorkGoal {
	private static final int MAX_BUILT = 10;
	private int task;   // 0 repareren, 1 bankje, 2 bloemen, 3 paddenstoel

	public BuildGoal(GnomeEntity gnome) {
		super(gnome);
	}

	@Override
	protected boolean findTarget(ServerLevel level) {
		if (this.gnome.materials() < 3 || !this.gnome.hasVillage() || !this.gnome.hasHome()) return false;
		VillageInfo info = VillageInfo.get(level, this.gnome.villageCenter());
		BlockPos best = null;
		double bd = Double.MAX_VALUE;
		for (BlockPos p : info.lampSockets) {
			if (level.getBlockState(p).isAir() && level.getBlockState(p.below()).is(Blocks.DARK_OAK_FENCE)) {
				double d = this.gnome.distanceToSqr(p.getX() + 0.5, p.getY(), p.getZ() + 0.5);
				if (d < bd) { bd = d; best = p; }
			}
		}
		if (best != null) {
			this.task = 0;
			this.target = best;
			this.stand = GnomeUtil.findStandNear(level, best).orElse(null);
			return this.stand != null;
		}
		if (this.gnome.builtCount() >= MAX_BUILT) return false;
		var rnd = this.gnome.getRandom();
		BlockPos home = this.gnome.home();
		for (int i = 0; i < 30; i++) {
			int x = home.getX() + rnd.nextInt(37) - 18;
			int z = home.getZ() + rnd.nextInt(37) - 18;
			if (!level.hasChunkAt(new BlockPos(x, home.getY(), z))) continue;
			for (int dy = 3; dy >= -3; dy--) {
				BlockPos p = new BlockPos(x, home.getY() + dy, z);
				BlockPos below = p.below();
				boolean free = level.getBlockState(p).isAir() && level.getBlockState(p.above()).isAir() && level.getBlockState(p.above(2)).isAir();
				boolean ground = level.getBlockState(below).is(Blocks.GRASS_BLOCK) || level.getBlockState(below).is(Blocks.PODZOL);
				if (free && ground) {
					var st = GnomeUtil.findStandNear(level, p);
					if (st.isEmpty()) return false;
					this.task = 1 + rnd.nextInt(3);
					this.target = p;
					this.stand = st.get();
					return true;
				}
			}
		}
		return false;
	}

	@Override
	protected int duration() {
		return 80;
	}

	@Override
	protected String animation() {
		return "work";
	}

	@Override
	protected int nextCooldown() {
		return 600 + this.gnome.getRandom().nextInt(900);
	}

	@Override
	protected void work(ServerLevel level, int t) {
		if (t % 20 == 10) {
			level.playSound(null, this.target, SoundEvents.ANVIL_USE, SoundSource.NEUTRAL, 0.3F, 1.5F);
			this.gnome.voice(ModSounds.WORK_BUILD, 0.7F);
		}
		if (t != 50 || !level.getBlockState(this.target).isAir()) return;
		var rnd = this.gnome.getRandom();
		switch (this.task) {
			case 0 -> {
				level.setBlock(this.target, ModBlocks.TOADSTOOL_LAMP.defaultBlockState(), 3);
				VillageInfo.get(level, this.gnome.villageCenter()).lampSockets.remove(this.target);
			}
			case 1 -> level.setBlock(this.target, Blocks.SPRUCE_STAIRS.defaultBlockState(), 3);
			case 2 -> {
				Object[] flowers = {Blocks.POPPY, Blocks.AZURE_BLUET, Blocks.CORNFLOWER, Blocks.DANDELION};
				for (int dx = -1; dx <= 1; dx++) {
					for (int dz = -1; dz <= 1; dz++) {
						BlockPos p = this.target.offset(dx, 0, dz);
						if ((dx == 0 && dz == 0) || rnd.nextInt(3) == 0) {
							if (level.getBlockState(p).isAir() && level.getBlockState(p.below()).is(Blocks.GRASS_BLOCK)) {
								level.setBlock(p, ((net.minecraft.world.level.block.Block) flowers[rnd.nextInt(flowers.length)]).defaultBlockState(), 3);
							}
						}
					}
				}
			}
			default -> {
				level.setBlock(this.target, ModBlocks.GNOME_STEM.defaultBlockState(), 3);
				level.setBlock(this.target.above(), ModBlocks.TOADSTOOL_CAP_SLAB.defaultBlockState(), 3);
			}
		}
		this.gnome.addMaterials(-3);
		if (this.task != 0) this.gnome.addBuilt();
	}
}
