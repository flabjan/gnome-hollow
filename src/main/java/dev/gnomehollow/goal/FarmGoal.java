package dev.gnomehollow.goal;

import dev.gnomehollow.entity.GnomeEntity;
import java.util.Optional;
import net.minecraft.core.BlockPos;
import dev.gnomehollow.ModSounds;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.CropBlock;
import net.minecraft.world.level.block.state.BlockState;

/** Farmer: oogst volgroeide gewassen (tarwe, wortels, aardappels, bieten) en plant meteen opnieuw. */
public class FarmGoal extends WorkGoal {
	public FarmGoal(GnomeEntity gnome) {
		super(gnome);
	}

	private static boolean mature(BlockState s) {
		return s.getBlock() instanceof CropBlock crop && crop.isMaxAge(s);
	}

	@Override
	protected boolean findTarget(ServerLevel level) {
		Optional<BlockPos> crop = GnomeUtil.findNearest(level, this.gnome.blockPosition(), 16, 2, FarmGoal::mature);
		if (crop.isEmpty()) return false;
		this.target = crop.get();
		this.stand = GnomeUtil.findStandNear(level, this.target).orElse(this.target);
		return true;
	}

	@Override
	protected boolean targetStillValid(ServerLevel level) {
		return mature(level.getBlockState(this.target));
	}

	@Override
	protected boolean celebrates() {
		return false;
	}

	@Override
	protected int duration() {
		return 50;
	}

	@Override
	protected String animation() {
		return "work";
	}

	@Override
	protected int nextCooldown() {
		return 15 + this.gnome.getRandom().nextInt(40);
	}

	@Override
	protected void work(ServerLevel level, int t) {
		if (t == 20) {
			BlockState state = level.getBlockState(this.target);
			if (state.getBlock() instanceof CropBlock crop && crop.isMaxAge(state)) {
				this.gnome.voice(ModSounds.WORK_FARM, 0.8F);
				// De oogst gaat naar de opslag bij het eigen huis (anders valt hij op de grond); daarna meteen opnieuw zaaien.
				net.minecraft.world.item.Item item = state.is(Blocks.CARROTS) ? Items.CARROT : state.is(Blocks.POTATOES) ? Items.POTATO
						: state.is(Blocks.BEETROOTS) ? Items.BEETROOT : Items.WHEAT;
				ItemStack drop = new ItemStack(item, 1 + this.gnome.getRandom().nextInt(3));
				BlockPos storage = this.gnome.hasHome() ? this.gnome.home() : this.gnome.blockPosition();
				if (!GnomeUtil.insertIntoNearbyContainer(level, storage, 14, drop)) this.gnome.spawnAtLocation(level, drop);
				level.setBlock(this.target, crop.getStateForAge(0), 3);
				level.playSound(null, this.target, SoundEvents.CROP_PLANTED, SoundSource.NEUTRAL, 0.8F, 1.0F);
			}
		}
	}
}
