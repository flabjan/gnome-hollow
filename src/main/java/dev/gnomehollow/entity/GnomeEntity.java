package dev.gnomehollow.entity;

import dev.gnomehollow.GnomeTrades;
import dev.gnomehollow.ModSounds;
import dev.gnomehollow.goal.AlertAvoidGoal;
import dev.gnomehollow.goal.BuildGoal;
import dev.gnomehollow.goal.FarmGoal;
import dev.gnomehollow.goal.FishGoal;
import dev.gnomehollow.goal.HealerBrewGoal;
import dev.gnomehollow.goal.MusicGoal;
import dev.gnomehollow.goal.NightHomeGoal;
import dev.gnomehollow.goal.StayNearHomeGoal;
import java.util.List;
import net.minecraft.core.BlockPos;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.entity.PathfinderMob;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.ai.goal.FloatGoal;
import net.minecraft.world.entity.ai.goal.LookAtPlayerGoal;
import net.minecraft.world.entity.ai.goal.MeleeAttackGoal;
import net.minecraft.world.entity.ai.goal.PanicGoal;
import net.minecraft.world.entity.ai.goal.RandomLookAroundGoal;
import net.minecraft.world.entity.ai.goal.WaterAvoidingRandomStrollGoal;
import net.minecraft.world.entity.ai.goal.target.HurtByTargetGoal;
import net.minecraft.world.entity.ai.goal.target.NearestAttackableTargetGoal;
import net.minecraft.world.entity.monster.Monster;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.trading.Merchant;
import net.minecraft.world.item.trading.MerchantOffer;
import net.minecraft.world.item.trading.MerchantOffers;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.storage.ValueInput;
import net.minecraft.world.level.storage.ValueOutput;
// GeckoLib 5.5+ gebruikt de basis-package com.geckolib (voorheen software.bernie.geckolib).
import com.geckolib.animatable.*;
import com.geckolib.animatable.instance.*;
import com.geckolib.animatable.manager.*;
import com.geckolib.animation.*;
import com.geckolib.animation.state.*;
import com.geckolib.util.*;

/**
 * Eén klasse voor alle gnomes. Het beroep volgt uit het EntityType (gnome_healer, gnome_warrior, ...),
 * zodat elk beroep een eigen model/texture kan krijgen zonder gesynchroniseerde data.
 */
public class GnomeEntity extends PathfinderMob implements GeoEntity, Merchant {
	private static final RawAnimation IDLE = RawAnimation.begin().thenLoop("animation.gnome.idle");
	private static final RawAnimation WALK = RawAnimation.begin().thenLoop("animation.gnome.walk");
	private static final RawAnimation ATTACK = RawAnimation.begin().thenPlay("animation.gnome.attack");
	// Werk-animaties zijn "play once" en worden door aiStep() steeds opnieuw gestart zolang het werk duurt;
	// zo is er geen "stop"-aanroep nodig (die API verschilt per GeckoLib-versie).
	private static final RawAnimation WORK = RawAnimation.begin().thenPlay("animation.gnome.work");
	private static final RawAnimation FISH = RawAnimation.begin().thenPlay("animation.gnome.fish");
	private static final RawAnimation PLAY = RawAnimation.begin().thenPlay("animation.gnome.play");
	private static final RawAnimation NONE = RawAnimation.begin().thenLoop("animation.gnome.none");

	private final AnimatableInstanceCache cache = GeckoLibUtil.createInstanceCache(this);
	private boolean homeSet;
	private BlockPos homePos;
	private int built;
	private boolean playingMusic;
	private String actionAnim;
	private int actionPeriod;
	private int greetCooldown = 100;
	private int lastVoiceTick = -1000;
	private Player tradingPlayer;
	private MerchantOffers offers;
	private int musicSong;
	private int musicPart;
	private long musicEnd;

	public GnomeEntity(EntityType<? extends GnomeEntity> type, Level level) {
		super(type, level);
		this.setPersistenceRequired();
	}

	public static AttributeSupplier.Builder createGnomeAttributes(Profession p) {
		boolean warrior = p == Profession.WARRIOR;
		return Mob.createMobAttributes()
				.add(Attributes.MAX_HEALTH, warrior ? 30.0 : 16.0)
				.add(Attributes.MOVEMENT_SPEED, 0.27)
				.add(Attributes.ATTACK_DAMAGE, warrior ? 5.0 : 1.0)
				.add(Attributes.FOLLOW_RANGE, 24.0)
				.add(Attributes.KNOCKBACK_RESISTANCE, warrior ? 0.3 : 0.0);
	}

	public Profession profession() {
		return Profession.fromType(this.getType());
	}

	@Override
	protected void registerGoals() {
		Profession p = Profession.fromType(this.getType());

		this.goalSelector.addGoal(0, new FloatGoal(this));
		this.targetSelector.addGoal(1, new HurtByTargetGoal(this).setAlertOthers());

		if (p == Profession.WARRIOR) {
			this.goalSelector.addGoal(1, new MeleeAttackGoal(this, 1.15, true));
			this.targetSelector.addGoal(2, new NearestAttackableTargetGoal<>(this, Monster.class, true));
		} else {
			this.goalSelector.addGoal(1, new PanicGoal(this, 1.4));
			this.goalSelector.addGoal(2, new AlertAvoidGoal(this, 8.0F, 0.8, 1.1));
		}

		switch (p) {
			case FISHERMAN -> this.goalSelector.addGoal(3, new FishGoal(this));
			case HEALER -> this.goalSelector.addGoal(3, new HealerBrewGoal(this));
			case FARMER -> this.goalSelector.addGoal(3, new FarmGoal(this));
			case BUILDER -> this.goalSelector.addGoal(3, new BuildGoal(this));
			case NITWIT -> { }
			case WARRIOR -> { }
		}

		this.goalSelector.addGoal(4, new StayNearHomeGoal(this, 28.0));
		if (p != Profession.WARRIOR) {
			this.goalSelector.addGoal(4, new NightHomeGoal(this));
		}
		this.goalSelector.addGoal(5, new MusicGoal(this));
		this.goalSelector.addGoal(6, new WaterAvoidingRandomStrollGoal(this, 0.6));
		this.goalSelector.addGoal(7, new LookAtPlayerGoal(this, Player.class, 6.0F));
		this.goalSelector.addGoal(8, new RandomLookAroundGoal(this));
	}

	@Override
	public void tick() {
		super.tick();
		if (!this.level().isClientSide() && !this.homeSet) {
			this.homeSet = true;
			this.homePos = this.blockPosition();
		}
	}

	@Override
	public void aiStep() {
		super.aiStep();
		// Healer: geneest gewonde spelers, dorpelingen, gnomes en golems in de buurt.
		if (!this.level().isClientSide() && this.level() instanceof ServerLevel server
				&& this.profession() == Profession.HEALER && this.tickCount % 40 == 0 && this.isAlive()) {
			List<LivingEntity> hurt = server.getEntitiesOfClass(LivingEntity.class, this.getBoundingBox().inflate(6.0),
					e -> e != this && e.isAlive() && e.getHealth() < e.getMaxHealth() - 2.0F
							&& (e instanceof Player || e instanceof GnomeEntity || isFriendlyType(e)));
			if (!hurt.isEmpty()) {
				LivingEntity patient = hurt.get(0);
				patient.heal(4.0F);
				server.sendParticles(ParticleTypes.HEART, patient.getX(), patient.getY() + patient.getBbHeight() + 0.2,
						patient.getZ(), 5, 0.3, 0.2, 0.3, 0.0);
				server.playSound(null, patient.blockPosition(), SoundEvents.AMETHYST_BLOCK_CHIME, SoundSource.NEUTRAL, 1.0F, 1.4F);
				this.triggerAnim("action", "work");
				this.voice(ModSounds.HEAL, 1.0F);
			}
		}
		// Tijdens het handelen blijft de gnome staan en kijkt naar de speler.
		if (!this.level().isClientSide() && this.tradingPlayer != null) {
			if (!this.tradingPlayer.isAlive() || this.distanceToSqr(this.tradingPlayer) > 100.0) {
				this.tradingPlayer = null;
			} else {
				this.getNavigation().stop();
				this.getLookControl().setLookAt(this.tradingPlayer);
			}
		}
		// Elke dag een nieuwe voorraad.
		if (!this.level().isClientSide() && this.tradingPlayer == null && this.tickCount % 24000 == 23999) {
			this.offers = null;
		}
		// Werk-animatie herhalen zolang de gnome aan het werk is.
		if (!this.level().isClientSide() && this.actionAnim != null && this.tickCount % this.actionPeriod == 0) {
			this.triggerAnim("action", this.actionAnim);
		}
		// Groeten: een vriendelijk "hii-hii!" als een speler dichtbij komt.
		if (!this.level().isClientSide() && this.isAlive()) {
			if (this.greetCooldown > 0) {
				this.greetCooldown--;
			} else if (this.tickCount % 20 == 0 && this.isWorkTime()) {
				Player p = this.level().getNearestPlayer(this, 4.0);
				if (p != null && !p.isSpectator() && this.hasLineOfSight(p)) {
					this.voice(ModSounds.GREET, 1.0F);
					this.greetCooldown = 2400 + this.random.nextInt(1200);
				}
			}
		}
	}

	@Override
	public void swing(InteractionHand hand) {
		if (!this.level().isClientSide()) {
			this.triggerAnim("action", "attack");
			if (this.profession() == Profession.WARRIOR && this.random.nextInt(3) == 0) {
				this.voice(ModSounds.ATTACK, 1.0F);
			}
		}
		super.swing(hand);
	}

	/** Dorpelingen en ijzergolems tellen mee als 'vriendelijk' voor de Healer (via registry-naam, versie-onafhankelijk). */
	private static boolean isFriendlyType(LivingEntity e) {
		String path = BuiltInRegistries.ENTITY_TYPE.getKey(e.getType()).getPath();
		return path.equals("villager") || path.equals("iron_golem");
	}

	// ---- helpers voor goals ----

	public boolean isWorkTime() {
		return this.level().isBrightOutside();
	}

	public BlockPos home() {
		return this.homePos;
	}

	public int builtCount() {
		return this.built;
	}

	public void addBuilt() {
		this.built++;
	}

	public boolean isPlayingMusic() {
		return this.playingMusic;
	}

	public void setPlayingMusic(boolean playing) {
		this.playingMusic = playing;
	}

	public void startAnim(String name) {
		if (!this.level().isClientSide()) {
			this.actionAnim = name;
			this.actionPeriod = switch (name) {
				case "fish" -> 60;
				case "play" -> 12;
				default -> 18;
			};
			this.triggerAnim("action", name);
		}
	}

	public void stopAnim() {
		// De laatste animatie speelt nog uit en stopt dan vanzelf.
		this.actionAnim = null;
	}

	// ---- opslaan ----

	@Override
	protected void addAdditionalSaveData(ValueOutput output) {
		super.addAdditionalSaveData(output);
		output.putInt("Built", this.built);
	}

	@Override
	protected void readAdditionalSaveData(ValueInput input) {
		super.readAdditionalSaveData(input);
		this.built = input.getIntOr("Built", 0);
	}

	@Override
	public boolean removeWhenFarAway(double distanceToClosestPlayer) {
		return false;
	}

	// ---- geluiden (eigen kabouterstem, zie ModSounds) ----

	/** Basis-toonhoogte per beroep: de krijger is wat dieper, de nitwit het schelst. */
	private float voicePitch() {
		return switch (this.profession()) {
			case WARRIOR -> 0.9F;
			case BUILDER -> 0.85F;
			case FISHERMAN -> 0.95F;
			case FARMER -> 1.0F;
			case HEALER -> 1.1F;
			case NITWIT -> 1.2F;
		};
	}

	/** Speelt een stemgeluid met een lichte willekeurige variatie af (alleen server-kant aanroepen). */
	public void voice(SoundEvent sound, float volume) {
		if (sound == null || this.level().isClientSide()) return;
		boolean important = sound == ModSounds.ATTACK || sound == ModSounds.ALERT || sound == ModSounds.YES
				|| sound == ModSounds.NO || sound == ModSounds.HEAL || sound == ModSounds.GREET;
		if (!important && this.tickCount - this.lastVoiceTick < 300) return;   // niet constant kwetteren
		this.lastVoiceTick = this.tickCount;
		this.playSound(sound, volume, this.voicePitch() + (this.random.nextFloat() - 0.5F) * 0.12F);
	}

	@Override
	protected SoundEvent getAmbientSound() {
		// 's Nachts bij huis: snurken in plaats van brabbelen.
		if (!this.isWorkTime() && this.homePos != null
				&& this.distanceToSqr(this.homePos.getX() + 0.5, this.homePos.getY(), this.homePos.getZ() + 0.5) < 36.0) {
			return ModSounds.SNORE;
		}
		// Alleen brabbelen als er een speler in de buurt is om het te horen.
		if (this.level().getNearestPlayer(this, 12.0) == null) return null;
		return ModSounds.AMBIENT;
	}

	@Override
	public int getAmbientSoundInterval() {
		return 1800;
	}

	@Override
	protected SoundEvent getHurtSound(DamageSource source) {
		return ModSounds.HURT;
	}

	@Override
	protected SoundEvent getDeathSound() {
		return ModSounds.DEATH;
	}

	@Override
	protected void playStepSound(BlockPos pos, BlockState state) {
		if (this.random.nextInt(2) == 0) {
			this.playSound(ModSounds.STEP, 0.2F, 0.9F + this.random.nextFloat() * 0.3F);
		}
	}

	@Override
	public void setTarget(LivingEntity target) {
		boolean newTarget = target != null && this.getTarget() == null;
		super.setTarget(target);
		if (newTarget && this.profession() == Profession.WARRIOR) {
			this.voice(ModSounds.ATTACK, 1.0F);
		}
	}

	/** Rechtsklik opent het handelsvenster (zoals bij dorpelingen). */
	@Override
	public InteractionResult mobInteract(Player player, InteractionHand hand) {
		if (!this.level().isClientSide() && this.isAlive() && this.tradingPlayer == null) {
			this.tradingPlayer = player;
			this.getLookControl().setLookAt(player);
			this.voice(ModSounds.YES, 1.0F);
			this.openTradingScreen(player, this.getDisplayName(), 1);
		}
		return InteractionResult.SUCCESS;
	}

	// ---- handel (Merchant) ----

	public boolean isTrading() {
		return this.tradingPlayer != null;
	}

	public void setTradingPlayer(Player player) {
		this.tradingPlayer = player;
	}

	public Player getTradingPlayer() {
		return this.tradingPlayer;
	}

	public MerchantOffers getOffers() {
		if (this.offers == null) {
			this.offers = new MerchantOffers();
			GnomeTrades.fill(this.offers, this.profession());
		}
		return this.offers;
	}

	public void overrideOffers(MerchantOffers newOffers) {
		this.offers = newOffers;
	}

	public void notifyTrade(MerchantOffer offer) {
		offer.increaseUses();
		this.voice(ModSounds.CELEBRATE, 1.0F);
	}

	public void notifyTradeUpdated(ItemStack stack) {
	}

	public int getVillagerXp() {
		return 0;
	}

	public void overrideXp(int xp) {
	}

	public boolean showProgressBar() {
		return false;
	}

	public SoundEvent getNotifyTradeSound() {
		return ModSounds.YES;
	}

	public boolean isClientSide() {
		return this.level().isClientSide();
	}

	// ---- samen muziek maken ----

	public int musicSong() {
		return this.musicSong;
	}

	public int musicPart() {
		return this.musicPart;
	}

	public long musicEnd() {
		return this.musicEnd;
	}

	public void setMusic(int song, int part, long endTick) {
		this.musicSong = song;
		this.musicPart = part;
		this.musicEnd = endTick;
	}

	// ---- GeckoLib ----

	@Override
	public void registerControllers(AnimatableManager.ControllerRegistrar controllers) {
		controllers.add(new AnimationController<GnomeEntity>("move", 4,
				state -> state.isMoving() ? state.setAndContinue(WALK) : state.setAndContinue(IDLE)));
		controllers.add(new AnimationController<GnomeEntity>("action", 2, state -> state.setAndContinue(NONE))
				.triggerableAnim("attack", ATTACK)
				.triggerableAnim("work", WORK)
				.triggerableAnim("fish", FISH)
				.triggerableAnim("play", PLAY));
	}

	@Override
	public AnimatableInstanceCache getAnimatableInstanceCache() {
		return this.cache;
	}
}
