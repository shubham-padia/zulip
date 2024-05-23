declare module 'astro:content' {
	interface Render {
		'.mdx': Promise<{
			Content: import('astro').MarkdownInstance<{}>['Content'];
			headings: import('astro').MarkdownHeading[];
			remarkPluginFrontmatter: Record<string, any>;
		}>;
	}
}

declare module 'astro:content' {
	interface Render {
		'.md': Promise<{
			Content: import('astro').MarkdownInstance<{}>['Content'];
			headings: import('astro').MarkdownHeading[];
			remarkPluginFrontmatter: Record<string, any>;
		}>;
	}
}

declare module 'astro:content' {
	type Flatten<T> = T extends { [K: string]: infer U } ? U : never;

	export type CollectionKey = keyof AnyEntryMap;
	export type CollectionEntry<C extends CollectionKey> = Flatten<AnyEntryMap[C]>;

	export type ContentCollectionKey = keyof ContentEntryMap;
	export type DataCollectionKey = keyof DataEntryMap;

	type AllValuesOf<T> = T extends any ? T[keyof T] : never;
	type ValidContentEntrySlug<C extends keyof ContentEntryMap> = AllValuesOf<
		ContentEntryMap[C]
	>['slug'];

	export function getEntryBySlug<
		C extends keyof ContentEntryMap,
		E extends ValidContentEntrySlug<C> | (string & {}),
	>(
		collection: C,
		// Note that this has to accept a regular string too, for SSR
		entrySlug: E
	): E extends ValidContentEntrySlug<C>
		? Promise<CollectionEntry<C>>
		: Promise<CollectionEntry<C> | undefined>;

	export function getDataEntryById<C extends keyof DataEntryMap, E extends keyof DataEntryMap[C]>(
		collection: C,
		entryId: E
	): Promise<CollectionEntry<C>>;

	export function getCollection<C extends keyof AnyEntryMap, E extends CollectionEntry<C>>(
		collection: C,
		filter?: (entry: CollectionEntry<C>) => entry is E
	): Promise<E[]>;
	export function getCollection<C extends keyof AnyEntryMap>(
		collection: C,
		filter?: (entry: CollectionEntry<C>) => unknown
	): Promise<CollectionEntry<C>[]>;

	export function getEntry<
		C extends keyof ContentEntryMap,
		E extends ValidContentEntrySlug<C> | (string & {}),
	>(entry: {
		collection: C;
		slug: E;
	}): E extends ValidContentEntrySlug<C>
		? Promise<CollectionEntry<C>>
		: Promise<CollectionEntry<C> | undefined>;
	export function getEntry<
		C extends keyof DataEntryMap,
		E extends keyof DataEntryMap[C] | (string & {}),
	>(entry: {
		collection: C;
		id: E;
	}): E extends keyof DataEntryMap[C]
		? Promise<DataEntryMap[C][E]>
		: Promise<CollectionEntry<C> | undefined>;
	export function getEntry<
		C extends keyof ContentEntryMap,
		E extends ValidContentEntrySlug<C> | (string & {}),
	>(
		collection: C,
		slug: E
	): E extends ValidContentEntrySlug<C>
		? Promise<CollectionEntry<C>>
		: Promise<CollectionEntry<C> | undefined>;
	export function getEntry<
		C extends keyof DataEntryMap,
		E extends keyof DataEntryMap[C] | (string & {}),
	>(
		collection: C,
		id: E
	): E extends keyof DataEntryMap[C]
		? Promise<DataEntryMap[C][E]>
		: Promise<CollectionEntry<C> | undefined>;

	/** Resolve an array of entry references from the same collection */
	export function getEntries<C extends keyof ContentEntryMap>(
		entries: {
			collection: C;
			slug: ValidContentEntrySlug<C>;
		}[]
	): Promise<CollectionEntry<C>[]>;
	export function getEntries<C extends keyof DataEntryMap>(
		entries: {
			collection: C;
			id: keyof DataEntryMap[C];
		}[]
	): Promise<CollectionEntry<C>[]>;

	export function reference<C extends keyof AnyEntryMap>(
		collection: C
	): import('astro/zod').ZodEffects<
		import('astro/zod').ZodString,
		C extends keyof ContentEntryMap
			? {
					collection: C;
					slug: ValidContentEntrySlug<C>;
				}
			: {
					collection: C;
					id: keyof DataEntryMap[C];
				}
	>;
	// Allow generic `string` to avoid excessive type errors in the config
	// if `dev` is not running to update as you edit.
	// Invalid collection names will be caught at build time.
	export function reference<C extends string>(
		collection: C
	): import('astro/zod').ZodEffects<import('astro/zod').ZodString, never>;

	type ReturnTypeOrOriginal<T> = T extends (...args: any[]) => infer R ? R : T;
	type InferEntrySchema<C extends keyof AnyEntryMap> = import('astro/zod').infer<
		ReturnTypeOrOriginal<Required<ContentConfig['collections'][C]>['schema']>
	>;

	type ContentEntryMap = {
		"docs": {
"add-a-bot-or-integration.mdx": {
	id: "add-a-bot-or-integration.mdx";
  slug: "add-a-bot-or-integration";
  body: string;
  collection: "docs";
  data: InferEntrySchema<"docs">
} & { render(): Render[".mdx"] };
"add-a-custom-linkifier.mdx": {
	id: "add-a-custom-linkifier.mdx";
  slug: "add-a-custom-linkifier";
  body: string;
  collection: "docs";
  data: InferEntrySchema<"docs">
} & { render(): Render[".mdx"] };
"add-or-remove-users-from-a-channel.mdx": {
	id: "add-or-remove-users-from-a-channel.mdx";
  slug: "add-or-remove-users-from-a-channel";
  body: string;
  collection: "docs";
  data: InferEntrySchema<"docs">
} & { render(): Render[".mdx"] };
"allow-image-link-previews.mdx": {
	id: "allow-image-link-previews.mdx";
  slug: "allow-image-link-previews";
  body: string;
  collection: "docs";
  data: InferEntrySchema<"docs">
} & { render(): Render[".mdx"] };
"analytics.mdx": {
	id: "analytics.mdx";
  slug: "analytics";
  body: string;
  collection: "docs";
  data: InferEntrySchema<"docs">
} & { render(): Render[".mdx"] };
"animated-gifs-from-giphy.mdx": {
	id: "animated-gifs-from-giphy.mdx";
  slug: "animated-gifs-from-giphy";
  body: string;
  collection: "docs";
  data: InferEntrySchema<"docs">
} & { render(): Render[".mdx"] };
"archive-a-channel.mdx": {
	id: "archive-a-channel.mdx";
  slug: "archive-a-channel";
  body: string;
  collection: "docs";
  data: InferEntrySchema<"docs">
} & { render(): Render[".mdx"] };
"bots-overview.mdx": {
	id: "bots-overview.mdx";
  slug: "bots-overview";
  body: string;
  collection: "docs";
  data: InferEntrySchema<"docs">
} & { render(): Render[".mdx"] };
"bulleted-lists.mdx": {
	id: "bulleted-lists.mdx";
  slug: "bulleted-lists";
  body: string;
  collection: "docs";
  data: InferEntrySchema<"docs">
} & { render(): Render[".mdx"] };
"change-a-users-name.mdx": {
	id: "change-a-users-name.mdx";
  slug: "change-a-users-name";
  body: string;
  collection: "docs";
  data: InferEntrySchema<"docs">
} & { render(): Render[".mdx"] };
"change-a-users-role.mdx": {
	id: "change-a-users-role.mdx";
  slug: "change-a-users-role";
  body: string;
  collection: "docs";
  data: InferEntrySchema<"docs">
} & { render(): Render[".mdx"] };
"change-organization-url.mdx": {
	id: "change-organization-url.mdx";
  slug: "change-organization-url";
  body: string;
  collection: "docs";
  data: InferEntrySchema<"docs">
} & { render(): Render[".mdx"] };
"change-the-channel-description.mdx": {
	id: "change-the-channel-description.mdx";
  slug: "change-the-channel-description";
  body: string;
  collection: "docs";
  data: InferEntrySchema<"docs">
} & { render(): Render[".mdx"] };
"change-the-color-of-a-channel.mdx": {
	id: "change-the-color-of-a-channel.mdx";
  slug: "change-the-color-of-a-channel";
  body: string;
  collection: "docs";
  data: InferEntrySchema<"docs">
} & { render(): Render[".mdx"] };
"change-the-privacy-of-a-channel.mdx": {
	id: "change-the-privacy-of-a-channel.mdx";
  slug: "change-the-privacy-of-a-channel";
  body: string;
  collection: "docs";
  data: InferEntrySchema<"docs">
} & { render(): Render[".mdx"] };
"change-the-time-format.mdx": {
	id: "change-the-time-format.mdx";
  slug: "change-the-time-format";
  body: string;
  collection: "docs";
  data: InferEntrySchema<"docs">
} & { render(): Render[".mdx"] };
"change-your-email-address.mdx": {
	id: "change-your-email-address.mdx";
  slug: "change-your-email-address";
  body: string;
  collection: "docs";
  data: InferEntrySchema<"docs">
} & { render(): Render[".mdx"] };
"change-your-language.mdx": {
	id: "change-your-language.mdx";
  slug: "change-your-language";
  body: string;
  collection: "docs";
  data: InferEntrySchema<"docs">
} & { render(): Render[".mdx"] };
"change-your-name.mdx": {
	id: "change-your-name.mdx";
  slug: "change-your-name";
  body: string;
  collection: "docs";
  data: InferEntrySchema<"docs">
} & { render(): Render[".mdx"] };
"change-your-password.mdx": {
	id: "change-your-password.mdx";
  slug: "change-your-password";
  body: string;
  collection: "docs";
  data: InferEntrySchema<"docs">
} & { render(): Render[".mdx"] };
"change-your-profile-picture.mdx": {
	id: "change-your-profile-picture.mdx";
  slug: "change-your-profile-picture";
  body: string;
  collection: "docs";
  data: InferEntrySchema<"docs">
} & { render(): Render[".mdx"] };
"change-your-timezone.mdx": {
	id: "change-your-timezone.mdx";
  slug: "change-your-timezone";
  body: string;
  collection: "docs";
  data: InferEntrySchema<"docs">
} & { render(): Render[".mdx"] };
"channel-notifications.mdx": {
	id: "channel-notifications.mdx";
  slug: "channel-notifications";
  body: string;
  collection: "docs";
  data: InferEntrySchema<"docs">
} & { render(): Render[".mdx"] };
"channel-permissions.mdx": {
	id: "channel-permissions.mdx";
  slug: "channel-permissions";
  body: string;
  collection: "docs";
  data: InferEntrySchema<"docs">
} & { render(): Render[".mdx"] };
"channel-posting-policy.mdx": {
	id: "channel-posting-policy.mdx";
  slug: "channel-posting-policy";
  body: string;
  collection: "docs";
  data: InferEntrySchema<"docs">
} & { render(): Render[".mdx"] };
"code-blocks.mdx": {
	id: "code-blocks.mdx";
  slug: "code-blocks";
  body: string;
  collection: "docs";
  data: InferEntrySchema<"docs">
} & { render(): Render[".mdx"] };
"collaborative-to-do-lists.mdx": {
	id: "collaborative-to-do-lists.mdx";
  slug: "collaborative-to-do-lists";
  body: string;
  collection: "docs";
  data: InferEntrySchema<"docs">
} & { render(): Render[".mdx"] };
"collapse-a-message.mdx": {
	id: "collapse-a-message.mdx";
  slug: "collapse-a-message";
  body: string;
  collection: "docs";
  data: InferEntrySchema<"docs">
} & { render(): Render[".mdx"] };
"combined-feed.mdx": {
	id: "combined-feed.mdx";
  slug: "combined-feed";
  body: string;
  collection: "docs";
  data: InferEntrySchema<"docs">
} & { render(): Render[".mdx"] };
"communities-directory.mdx": {
	id: "communities-directory.mdx";
  slug: "communities-directory";
  body: string;
  collection: "docs";
  data: InferEntrySchema<"docs">
} & { render(): Render[".mdx"] };
"configure-authentication-methods.mdx": {
	id: "configure-authentication-methods.mdx";
  slug: "configure-authentication-methods";
  body: string;
  collection: "docs";
  data: InferEntrySchema<"docs">
} & { render(): Render[".mdx"] };
"configure-automated-notices.mdx": {
	id: "configure-automated-notices.mdx";
  slug: "configure-automated-notices";
  body: string;
  collection: "docs";
  data: InferEntrySchema<"docs">
} & { render(): Render[".mdx"] };
"configure-default-new-user-settings.mdx": {
	id: "configure-default-new-user-settings.mdx";
  slug: "configure-default-new-user-settings";
  body: string;
  collection: "docs";
  data: InferEntrySchema<"docs">
} & { render(): Render[".mdx"] };
"configure-email-visibility.mdx": {
	id: "configure-email-visibility.mdx";
  slug: "configure-email-visibility";
  body: string;
  collection: "docs";
  data: InferEntrySchema<"docs">
} & { render(): Render[".mdx"] };
"configure-emoticon-translations.mdx": {
	id: "configure-emoticon-translations.mdx";
  slug: "configure-emoticon-translations";
  body: string;
  collection: "docs";
  data: InferEntrySchema<"docs">
} & { render(): Render[".mdx"] };
"configure-home-view.mdx": {
	id: "configure-home-view.mdx";
  slug: "configure-home-view";
  body: string;
  collection: "docs";
  data: InferEntrySchema<"docs">
} & { render(): Render[".mdx"] };
"configure-how-links-open.mdx": {
	id: "configure-how-links-open.mdx";
  slug: "configure-how-links-open";
  body: string;
  collection: "docs";
  data: InferEntrySchema<"docs">
} & { render(): Render[".mdx"] };
"configure-multi-language-search.mdx": {
	id: "configure-multi-language-search.mdx";
  slug: "configure-multi-language-search";
  body: string;
  collection: "docs";
  data: InferEntrySchema<"docs">
} & { render(): Render[".mdx"] };
"configure-organization-language.mdx": {
	id: "configure-organization-language.mdx";
  slug: "configure-organization-language";
  body: string;
  collection: "docs";
  data: InferEntrySchema<"docs">
} & { render(): Render[".mdx"] };
"configure-unread-message-counters.mdx": {
	id: "configure-unread-message-counters.mdx";
  slug: "configure-unread-message-counters";
  body: string;
  collection: "docs";
  data: InferEntrySchema<"docs">
} & { render(): Render[".mdx"] };
"configure-who-can-create-channels.mdx": {
	id: "configure-who-can-create-channels.mdx";
  slug: "configure-who-can-create-channels";
  body: string;
  collection: "docs";
  data: InferEntrySchema<"docs">
} & { render(): Render[".mdx"] };
"configure-who-can-invite-to-channels.mdx": {
	id: "configure-who-can-invite-to-channels.mdx";
  slug: "configure-who-can-invite-to-channels";
  body: string;
  collection: "docs";
  data: InferEntrySchema<"docs">
} & { render(): Render[".mdx"] };
"connect-through-a-proxy.mdx": {
	id: "connect-through-a-proxy.mdx";
  slug: "connect-through-a-proxy";
  body: string;
  collection: "docs";
  data: InferEntrySchema<"docs">
} & { render(): Render[".mdx"] };
"contact-support.mdx": {
	id: "contact-support.mdx";
  slug: "contact-support";
  body: string;
  collection: "docs";
  data: InferEntrySchema<"docs">
} & { render(): Render[".mdx"] };
"create-a-channel.mdx": {
	id: "create-a-channel.mdx";
  slug: "create-a-channel";
  body: string;
  collection: "docs";
  data: InferEntrySchema<"docs">
} & { render(): Render[".mdx"] };
"create-a-poll.mdx": {
	id: "create-a-poll.mdx";
  slug: "create-a-poll";
  body: string;
  collection: "docs";
  data: InferEntrySchema<"docs">
} & { render(): Render[".mdx"] };
"create-channels.mdx": {
	id: "create-channels.mdx";
  slug: "create-channels";
  body: string;
  collection: "docs";
  data: InferEntrySchema<"docs">
} & { render(): Render[".mdx"] };
"create-user-groups.mdx": {
	id: "create-user-groups.mdx";
  slug: "create-user-groups";
  body: string;
  collection: "docs";
  data: InferEntrySchema<"docs">
} & { render(): Render[".mdx"] };
"create-your-organization-profile.mdx": {
	id: "create-your-organization-profile.mdx";
  slug: "create-your-organization-profile";
  body: string;
  collection: "docs";
  data: InferEntrySchema<"docs">
} & { render(): Render[".mdx"] };
"custom-certificates.mdx": {
	id: "custom-certificates.mdx";
  slug: "custom-certificates";
  body: string;
  collection: "docs";
  data: InferEntrySchema<"docs">
} & { render(): Render[".mdx"] };
"custom-emoji.mdx": {
	id: "custom-emoji.mdx";
  slug: "custom-emoji";
  body: string;
  collection: "docs";
  data: InferEntrySchema<"docs">
} & { render(): Render[".mdx"] };
"custom-profile-fields.mdx": {
	id: "custom-profile-fields.mdx";
  slug: "custom-profile-fields";
  body: string;
  collection: "docs";
  data: InferEntrySchema<"docs">
} & { render(): Render[".mdx"] };
"customize-organization-settings.mdx": {
	id: "customize-organization-settings.mdx";
  slug: "customize-organization-settings";
  body: string;
  collection: "docs";
  data: InferEntrySchema<"docs">
} & { render(): Render[".mdx"] };
"customize-settings-for-new-users.mdx": {
	id: "customize-settings-for-new-users.mdx";
  slug: "customize-settings-for-new-users";
  body: string;
  collection: "docs";
  data: InferEntrySchema<"docs">
} & { render(): Render[".mdx"] };
"dark-theme.mdx": {
	id: "dark-theme.mdx";
  slug: "dark-theme";
  body: string;
  collection: "docs";
  data: InferEntrySchema<"docs">
} & { render(): Render[".mdx"] };
"deactivate-or-reactivate-a-bot.mdx": {
	id: "deactivate-or-reactivate-a-bot.mdx";
  slug: "deactivate-or-reactivate-a-bot";
  body: string;
  collection: "docs";
  data: InferEntrySchema<"docs">
} & { render(): Render[".mdx"] };
"deactivate-or-reactivate-a-user.mdx": {
	id: "deactivate-or-reactivate-a-user.mdx";
  slug: "deactivate-or-reactivate-a-user";
  body: string;
  collection: "docs";
  data: InferEntrySchema<"docs">
} & { render(): Render[".mdx"] };
"deactivate-your-account.mdx": {
	id: "deactivate-your-account.mdx";
  slug: "deactivate-your-account";
  body: string;
  collection: "docs";
  data: InferEntrySchema<"docs">
} & { render(): Render[".mdx"] };
"deactivate-your-organization.mdx": {
	id: "deactivate-your-organization.mdx";
  slug: "deactivate-your-organization";
  body: string;
  collection: "docs";
  data: InferEntrySchema<"docs">
} & { render(): Render[".mdx"] };
"delete-a-message.mdx": {
	id: "delete-a-message.mdx";
  slug: "delete-a-message";
  body: string;
  collection: "docs";
  data: InferEntrySchema<"docs">
} & { render(): Render[".mdx"] };
"delete-a-topic.mdx": {
	id: "delete-a-topic.mdx";
  slug: "delete-a-topic";
  body: string;
  collection: "docs";
  data: InferEntrySchema<"docs">
} & { render(): Render[".mdx"] };
"demo-organizations.mdx": {
	id: "demo-organizations.mdx";
  slug: "demo-organizations";
  body: string;
  collection: "docs";
  data: InferEntrySchema<"docs">
} & { render(): Render[".mdx"] };
"desktop-app-install-guide.mdx": {
	id: "desktop-app-install-guide.mdx";
  slug: "desktop-app-install-guide";
  body: string;
  collection: "docs";
  data: InferEntrySchema<"docs">
} & { render(): Render[".mdx"] };
"desktop-notifications.mdx": {
	id: "desktop-notifications.mdx";
  slug: "desktop-notifications";
  body: string;
  collection: "docs";
  data: InferEntrySchema<"docs">
} & { render(): Render[".mdx"] };
"digest-emails.mdx": {
	id: "digest-emails.mdx";
  slug: "digest-emails";
  body: string;
  collection: "docs";
  data: InferEntrySchema<"docs">
} & { render(): Render[".mdx"] };
"direct-messages.mdx": {
	id: "direct-messages.mdx";
  slug: "direct-messages";
  body: string;
  collection: "docs";
  data: InferEntrySchema<"docs">
} & { render(): Render[".mdx"] };
"disable-message-edit-history.mdx": {
	id: "disable-message-edit-history.mdx";
  slug: "disable-message-edit-history";
  body: string;
  collection: "docs";
  data: InferEntrySchema<"docs">
} & { render(): Render[".mdx"] };
"disable-welcome-emails.mdx": {
	id: "disable-welcome-emails.mdx";
  slug: "disable-welcome-emails";
  body: string;
  collection: "docs";
  data: InferEntrySchema<"docs">
} & { render(): Render[".mdx"] };
"dm-mention-alert-notifications.mdx": {
	id: "dm-mention-alert-notifications.mdx";
  slug: "dm-mention-alert-notifications";
  body: string;
  collection: "docs";
  data: InferEntrySchema<"docs">
} & { render(): Render[".mdx"] };
"do-not-disturb.mdx": {
	id: "do-not-disturb.mdx";
  slug: "do-not-disturb";
  body: string;
  collection: "docs";
  data: InferEntrySchema<"docs">
} & { render(): Render[".mdx"] };
"edit-a-bot.mdx": {
	id: "edit-a-bot.mdx";
  slug: "edit-a-bot";
  body: string;
  collection: "docs";
  data: InferEntrySchema<"docs">
} & { render(): Render[".mdx"] };
"edit-a-message.mdx": {
	id: "edit-a-message.mdx";
  slug: "edit-a-message";
  body: string;
  collection: "docs";
  data: InferEntrySchema<"docs">
} & { render(): Render[".mdx"] };
"edit-your-profile.mdx": {
	id: "edit-your-profile.mdx";
  slug: "edit-your-profile";
  body: string;
  collection: "docs";
  data: InferEntrySchema<"docs">
} & { render(): Render[".mdx"] };
"email-notifications.mdx": {
	id: "email-notifications.mdx";
  slug: "email-notifications";
  body: string;
  collection: "docs";
  data: InferEntrySchema<"docs">
} & { render(): Render[".mdx"] };
"emoji-and-emoticons.mdx": {
	id: "emoji-and-emoticons.mdx";
  slug: "emoji-and-emoticons";
  body: string;
  collection: "docs";
  data: InferEntrySchema<"docs">
} & { render(): Render[".mdx"] };
"emoji-reactions.mdx": {
	id: "emoji-reactions.mdx";
  slug: "emoji-reactions";
  body: string;
  collection: "docs";
  data: InferEntrySchema<"docs">
} & { render(): Render[".mdx"] };
"enable-full-width-display.mdx": {
	id: "enable-full-width-display.mdx";
  slug: "enable-full-width-display";
  body: string;
  collection: "docs";
  data: InferEntrySchema<"docs">
} & { render(): Render[".mdx"] };
"export-your-organization.mdx": {
	id: "export-your-organization.mdx";
  slug: "export-your-organization";
  body: string;
  collection: "docs";
  data: InferEntrySchema<"docs">
} & { render(): Render[".mdx"] };
"find-administrators.mdx": {
	id: "find-administrators.mdx";
  slug: "find-administrators";
  body: string;
  collection: "docs";
  data: InferEntrySchema<"docs">
} & { render(): Render[".mdx"] };
"finding-a-conversation-to-read.mdx": {
	id: "finding-a-conversation-to-read.mdx";
  slug: "finding-a-conversation-to-read";
  body: string;
  collection: "docs";
  data: InferEntrySchema<"docs">
} & { render(): Render[".mdx"] };
"follow-a-topic.mdx": {
	id: "follow-a-topic.mdx";
  slug: "follow-a-topic";
  body: string;
  collection: "docs";
  data: InferEntrySchema<"docs">
} & { render(): Render[".mdx"] };
"font-size.mdx": {
	id: "font-size.mdx";
  slug: "font-size";
  body: string;
  collection: "docs";
  data: InferEntrySchema<"docs">
} & { render(): Render[".mdx"] };
"format-a-quote.mdx": {
	id: "format-a-quote.mdx";
  slug: "format-a-quote";
  body: string;
  collection: "docs";
  data: InferEntrySchema<"docs">
} & { render(): Render[".mdx"] };
"format-your-message-using-markdown.mdx": {
	id: "format-your-message-using-markdown.mdx";
  slug: "format-your-message-using-markdown";
  body: string;
  collection: "docs";
  data: InferEntrySchema<"docs">
} & { render(): Render[".mdx"] };
"gdpr-compliance.mdx": {
	id: "gdpr-compliance.mdx";
  slug: "gdpr-compliance";
  body: string;
  collection: "docs";
  data: InferEntrySchema<"docs">
} & { render(): Render[".mdx"] };
"generate-integration-url.mdx": {
	id: "generate-integration-url.mdx";
  slug: "generate-integration-url";
  body: string;
  collection: "docs";
  data: InferEntrySchema<"docs">
} & { render(): Render[".mdx"] };
"getting-started-with-zulip.mdx": {
	id: "getting-started-with-zulip.mdx";
  slug: "getting-started-with-zulip";
  body: string;
  collection: "docs";
  data: InferEntrySchema<"docs">
} & { render(): Render[".mdx"] };
"getting-your-organization-started-with-zulip.mdx": {
	id: "getting-your-organization-started-with-zulip.mdx";
  slug: "getting-your-organization-started-with-zulip";
  body: string;
  collection: "docs";
  data: InferEntrySchema<"docs">
} & { render(): Render[".mdx"] };
"global-times.mdx": {
	id: "global-times.mdx";
  slug: "global-times";
  body: string;
  collection: "docs";
  data: InferEntrySchema<"docs">
} & { render(): Render[".mdx"] };
"guest-users.mdx": {
	id: "guest-users.mdx";
  slug: "guest-users";
  body: string;
  collection: "docs";
  data: InferEntrySchema<"docs">
} & { render(): Render[".mdx"] };
"hide-message-content-in-emails.mdx": {
	id: "hide-message-content-in-emails.mdx";
  slug: "hide-message-content-in-emails";
  body: string;
  collection: "docs";
  data: InferEntrySchema<"docs">
} & { render(): Render[".mdx"] };
"high-contrast-mode.mdx": {
	id: "high-contrast-mode.mdx";
  slug: "high-contrast-mode";
  body: string;
  collection: "docs";
  data: InferEntrySchema<"docs">
} & { render(): Render[".mdx"] };
"import-from-mattermost.mdx": {
	id: "import-from-mattermost.mdx";
  slug: "import-from-mattermost";
  body: string;
  collection: "docs";
  data: InferEntrySchema<"docs">
} & { render(): Render[".mdx"] };
"import-from-rocketchat.mdx": {
	id: "import-from-rocketchat.mdx";
  slug: "import-from-rocketchat";
  body: string;
  collection: "docs";
  data: InferEntrySchema<"docs">
} & { render(): Render[".mdx"] };
"import-from-slack.mdx": {
	id: "import-from-slack.mdx";
  slug: "import-from-slack";
  body: string;
  collection: "docs";
  data: InferEntrySchema<"docs">
} & { render(): Render[".mdx"] };
"import-your-settings.mdx": {
	id: "import-your-settings.mdx";
  slug: "import-your-settings";
  body: string;
  collection: "docs";
  data: InferEntrySchema<"docs">
} & { render(): Render[".mdx"] };
"inbox.mdx": {
	id: "inbox.mdx";
  slug: "inbox";
  body: string;
  collection: "docs";
  data: InferEntrySchema<"docs">
} & { render(): Render[".mdx"] };
"include/select-channel-view-subscribers.md": {
	id: "include/select-channel-view-subscribers.md";
  slug: "include/select-channel-view-subscribers";
  body: string;
  collection: "docs";
  data: InferEntrySchema<"docs">
} & { render(): Render[".md"] };
"index.mdx": {
	id: "index.mdx";
  slug: "index";
  body: string;
  collection: "docs";
  data: InferEntrySchema<"docs">
} & { render(): Render[".mdx"] };
"insert-a-link.mdx": {
	id: "insert-a-link.mdx";
  slug: "insert-a-link";
  body: string;
  collection: "docs";
  data: InferEntrySchema<"docs">
} & { render(): Render[".mdx"] };
"integrations-overview.mdx": {
	id: "integrations-overview.mdx";
  slug: "integrations-overview";
  body: string;
  collection: "docs";
  data: InferEntrySchema<"docs">
} & { render(): Render[".mdx"] };
"introduction-to-channels.mdx": {
	id: "introduction-to-channels.mdx";
  slug: "introduction-to-channels";
  body: string;
  collection: "docs";
  data: InferEntrySchema<"docs">
} & { render(): Render[".mdx"] };
"introduction-to-topics.mdx": {
	id: "introduction-to-topics.mdx";
  slug: "introduction-to-topics";
  body: string;
  collection: "docs";
  data: InferEntrySchema<"docs">
} & { render(): Render[".mdx"] };
"invite-new-users.mdx": {
	id: "invite-new-users.mdx";
  slug: "invite-new-users";
  body: string;
  collection: "docs";
  data: InferEntrySchema<"docs">
} & { render(): Render[".mdx"] };
"invite-users-to-join.mdx": {
	id: "invite-users-to-join.mdx";
  slug: "invite-users-to-join";
  body: string;
  collection: "docs";
  data: InferEntrySchema<"docs">
} & { render(): Render[".mdx"] };
"join-a-zulip-organization.mdx": {
	id: "join-a-zulip-organization.mdx";
  slug: "join-a-zulip-organization";
  body: string;
  collection: "docs";
  data: InferEntrySchema<"docs">
} & { render(): Render[".mdx"] };
"keyboard-shortcuts.mdx": {
	id: "keyboard-shortcuts.mdx";
  slug: "keyboard-shortcuts";
  body: string;
  collection: "docs";
  data: InferEntrySchema<"docs">
} & { render(): Render[".mdx"] };
"latex.mdx": {
	id: "latex.mdx";
  slug: "latex";
  body: string;
  collection: "docs";
  data: InferEntrySchema<"docs">
} & { render(): Render[".mdx"] };
"link-to-a-message-or-conversation.mdx": {
	id: "link-to-a-message-or-conversation.mdx";
  slug: "link-to-a-message-or-conversation";
  body: string;
  collection: "docs";
  data: InferEntrySchema<"docs">
} & { render(): Render[".mdx"] };
"linking-to-zulip-website.mdx": {
	id: "linking-to-zulip-website.mdx";
  slug: "linking-to-zulip-website";
  body: string;
  collection: "docs";
  data: InferEntrySchema<"docs">
} & { render(): Render[".mdx"] };
"linking-to-zulip.mdx": {
	id: "linking-to-zulip.mdx";
  slug: "linking-to-zulip";
  body: string;
  collection: "docs";
  data: InferEntrySchema<"docs">
} & { render(): Render[".mdx"] };
"logging-in.mdx": {
	id: "logging-in.mdx";
  slug: "logging-in";
  body: string;
  collection: "docs";
  data: InferEntrySchema<"docs">
} & { render(): Render[".mdx"] };
"logging-out.mdx": {
	id: "logging-out.mdx";
  slug: "logging-out";
  body: string;
  collection: "docs";
  data: InferEntrySchema<"docs">
} & { render(): Render[".mdx"] };
"manage-a-user.mdx": {
	id: "manage-a-user.mdx";
  slug: "manage-a-user";
  body: string;
  collection: "docs";
  data: InferEntrySchema<"docs">
} & { render(): Render[".mdx"] };
"manage-inactive-channels.mdx": {
	id: "manage-inactive-channels.mdx";
  slug: "manage-inactive-channels";
  body: string;
  collection: "docs";
  data: InferEntrySchema<"docs">
} & { render(): Render[".mdx"] };
"manage-user-channel-subscriptions.mdx": {
	id: "manage-user-channel-subscriptions.mdx";
  slug: "manage-user-channel-subscriptions";
  body: string;
  collection: "docs";
  data: InferEntrySchema<"docs">
} & { render(): Render[".mdx"] };
"manage-user-groups.mdx": {
	id: "manage-user-groups.mdx";
  slug: "manage-user-groups";
  body: string;
  collection: "docs";
  data: InferEntrySchema<"docs">
} & { render(): Render[".mdx"] };
"manage-your-uploaded-files.mdx": {
	id: "manage-your-uploaded-files.mdx";
  slug: "manage-your-uploaded-files";
  body: string;
  collection: "docs";
  data: InferEntrySchema<"docs">
} & { render(): Render[".mdx"] };
"marking-messages-as-read.mdx": {
	id: "marking-messages-as-read.mdx";
  slug: "marking-messages-as-read";
  body: string;
  collection: "docs";
  data: InferEntrySchema<"docs">
} & { render(): Render[".mdx"] };
"marking-messages-as-unread.mdx": {
	id: "marking-messages-as-unread.mdx";
  slug: "marking-messages-as-unread";
  body: string;
  collection: "docs";
  data: InferEntrySchema<"docs">
} & { render(): Render[".mdx"] };
"mastering-the-compose-box.mdx": {
	id: "mastering-the-compose-box.mdx";
  slug: "mastering-the-compose-box";
  body: string;
  collection: "docs";
  data: InferEntrySchema<"docs">
} & { render(): Render[".mdx"] };
"me-action-messages.mdx": {
	id: "me-action-messages.mdx";
  slug: "me-action-messages";
  body: string;
  collection: "docs";
  data: InferEntrySchema<"docs">
} & { render(): Render[".mdx"] };
"mention-a-user-or-group.mdx": {
	id: "mention-a-user-or-group.mdx";
  slug: "mention-a-user-or-group";
  body: string;
  collection: "docs";
  data: InferEntrySchema<"docs">
} & { render(): Render[".mdx"] };
"message-a-channel-by-email.mdx": {
	id: "message-a-channel-by-email.mdx";
  slug: "message-a-channel-by-email";
  body: string;
  collection: "docs";
  data: InferEntrySchema<"docs">
} & { render(): Render[".mdx"] };
"message-actions.mdx": {
	id: "message-actions.mdx";
  slug: "message-actions";
  body: string;
  collection: "docs";
  data: InferEntrySchema<"docs">
} & { render(): Render[".mdx"] };
"message-retention-policy.mdx": {
	id: "message-retention-policy.mdx";
  slug: "message-retention-policy";
  body: string;
  collection: "docs";
  data: InferEntrySchema<"docs">
} & { render(): Render[".mdx"] };
"messaging-tips.mdx": {
	id: "messaging-tips.mdx";
  slug: "messaging-tips";
  body: string;
  collection: "docs";
  data: InferEntrySchema<"docs">
} & { render(): Render[".mdx"] };
"migrating-from-other-chat-tools.mdx": {
	id: "migrating-from-other-chat-tools.mdx";
  slug: "migrating-from-other-chat-tools";
  body: string;
  collection: "docs";
  data: InferEntrySchema<"docs">
} & { render(): Render[".mdx"] };
"missing.mdx": {
	id: "missing.mdx";
  slug: "missing";
  body: string;
  collection: "docs";
  data: InferEntrySchema<"docs">
} & { render(): Render[".mdx"] };
"mobile-notifications.mdx": {
	id: "mobile-notifications.mdx";
  slug: "mobile-notifications";
  body: string;
  collection: "docs";
  data: InferEntrySchema<"docs">
} & { render(): Render[".mdx"] };
"moderating-open-organizations.mdx": {
	id: "moderating-open-organizations.mdx";
  slug: "moderating-open-organizations";
  body: string;
  collection: "docs";
  data: InferEntrySchema<"docs">
} & { render(): Render[".mdx"] };
"move-content-to-another-channel.mdx": {
	id: "move-content-to-another-channel.mdx";
  slug: "move-content-to-another-channel";
  body: string;
  collection: "docs";
  data: InferEntrySchema<"docs">
} & { render(): Render[".mdx"] };
"move-content-to-another-topic.mdx": {
	id: "move-content-to-another-topic.mdx";
  slug: "move-content-to-another-topic";
  body: string;
  collection: "docs";
  data: InferEntrySchema<"docs">
} & { render(): Render[".mdx"] };
"mute-a-channel.mdx": {
	id: "mute-a-channel.mdx";
  slug: "mute-a-channel";
  body: string;
  collection: "docs";
  data: InferEntrySchema<"docs">
} & { render(): Render[".mdx"] };
"mute-a-topic.mdx": {
	id: "mute-a-topic.mdx";
  slug: "mute-a-topic";
  body: string;
  collection: "docs";
  data: InferEntrySchema<"docs">
} & { render(): Render[".mdx"] };
"mute-a-user.mdx": {
	id: "mute-a-user.mdx";
  slug: "mute-a-user";
  body: string;
  collection: "docs";
  data: InferEntrySchema<"docs">
} & { render(): Render[".mdx"] };
"numbered-lists.mdx": {
	id: "numbered-lists.mdx";
  slug: "numbered-lists";
  body: string;
  collection: "docs";
  data: InferEntrySchema<"docs">
} & { render(): Render[".mdx"] };
"open-the-compose-box.mdx": {
	id: "open-the-compose-box.mdx";
  slug: "open-the-compose-box";
  body: string;
  collection: "docs";
  data: InferEntrySchema<"docs">
} & { render(): Render[".mdx"] };
"organization-type.mdx": {
	id: "organization-type.mdx";
  slug: "organization-type";
  body: string;
  collection: "docs";
  data: InferEntrySchema<"docs">
} & { render(): Render[".mdx"] };
"paragraph-and-section-formatting.mdx": {
	id: "paragraph-and-section-formatting.mdx";
  slug: "paragraph-and-section-formatting";
  body: string;
  collection: "docs";
  data: InferEntrySchema<"docs">
} & { render(): Render[".mdx"] };
"pin-a-channel.mdx": {
	id: "pin-a-channel.mdx";
  slug: "pin-a-channel";
  body: string;
  collection: "docs";
  data: InferEntrySchema<"docs">
} & { render(): Render[".mdx"] };
"preview-your-message-before-sending.mdx": {
	id: "preview-your-message-before-sending.mdx";
  slug: "preview-your-message-before-sending";
  body: string;
  collection: "docs";
  data: InferEntrySchema<"docs">
} & { render(): Render[".mdx"] };
"printing-messages.mdx": {
	id: "printing-messages.mdx";
  slug: "printing-messages";
  body: string;
  collection: "docs";
  data: InferEntrySchema<"docs">
} & { render(): Render[".mdx"] };
"public-access-option.mdx": {
	id: "public-access-option.mdx";
  slug: "public-access-option";
  body: string;
  collection: "docs";
  data: InferEntrySchema<"docs">
} & { render(): Render[".mdx"] };
"quote-and-reply.mdx": {
	id: "quote-and-reply.mdx";
  slug: "quote-and-reply";
  body: string;
  collection: "docs";
  data: InferEntrySchema<"docs">
} & { render(): Render[".mdx"] };
"read-receipts.mdx": {
	id: "read-receipts.mdx";
  slug: "read-receipts";
  body: string;
  collection: "docs";
  data: InferEntrySchema<"docs">
} & { render(): Render[".mdx"] };
"reading-conversations.mdx": {
	id: "reading-conversations.mdx";
  slug: "reading-conversations";
  body: string;
  collection: "docs";
  data: InferEntrySchema<"docs">
} & { render(): Render[".mdx"] };
"reading-dms.mdx": {
	id: "reading-dms.mdx";
  slug: "reading-dms";
  body: string;
  collection: "docs";
  data: InferEntrySchema<"docs">
} & { render(): Render[".mdx"] };
"reading-strategies.mdx": {
	id: "reading-strategies.mdx";
  slug: "reading-strategies";
  body: string;
  collection: "docs";
  data: InferEntrySchema<"docs">
} & { render(): Render[".mdx"] };
"recent-conversations.mdx": {
	id: "recent-conversations.mdx";
  slug: "recent-conversations";
  body: string;
  collection: "docs";
  data: InferEntrySchema<"docs">
} & { render(): Render[".mdx"] };
"rename-a-channel.mdx": {
	id: "rename-a-channel.mdx";
  slug: "rename-a-channel";
  body: string;
  collection: "docs";
  data: InferEntrySchema<"docs">
} & { render(): Render[".mdx"] };
"rename-a-topic.mdx": {
	id: "rename-a-topic.mdx";
  slug: "rename-a-topic";
  body: string;
  collection: "docs";
  data: InferEntrySchema<"docs">
} & { render(): Render[".mdx"] };
"replying-to-messages.mdx": {
	id: "replying-to-messages.mdx";
  slug: "replying-to-messages";
  body: string;
  collection: "docs";
  data: InferEntrySchema<"docs">
} & { render(): Render[".mdx"] };
"request-an-integration.mdx": {
	id: "request-an-integration.mdx";
  slug: "request-an-integration";
  body: string;
  collection: "docs";
  data: InferEntrySchema<"docs">
} & { render(): Render[".mdx"] };
"require-topics.mdx": {
	id: "require-topics.mdx";
  slug: "require-topics";
  body: string;
  collection: "docs";
  data: InferEntrySchema<"docs">
} & { render(): Render[".mdx"] };
"resize-the-compose-box.mdx": {
	id: "resize-the-compose-box.mdx";
  slug: "resize-the-compose-box";
  body: string;
  collection: "docs";
  data: InferEntrySchema<"docs">
} & { render(): Render[".mdx"] };
"resolve-a-topic.mdx": {
	id: "resolve-a-topic.mdx";
  slug: "resolve-a-topic";
  body: string;
  collection: "docs";
  data: InferEntrySchema<"docs">
} & { render(): Render[".mdx"] };
"restrict-account-creation.mdx": {
	id: "restrict-account-creation.mdx";
  slug: "restrict-account-creation";
  body: string;
  collection: "docs";
  data: InferEntrySchema<"docs">
} & { render(): Render[".mdx"] };
"restrict-bot-creation.mdx": {
	id: "restrict-bot-creation.mdx";
  slug: "restrict-bot-creation";
  body: string;
  collection: "docs";
  data: InferEntrySchema<"docs">
} & { render(): Render[".mdx"] };
"restrict-direct-messages.mdx": {
	id: "restrict-direct-messages.mdx";
  slug: "restrict-direct-messages";
  body: string;
  collection: "docs";
  data: InferEntrySchema<"docs">
} & { render(): Render[".mdx"] };
"restrict-message-editing-and-deletion.mdx": {
	id: "restrict-message-editing-and-deletion.mdx";
  slug: "restrict-message-editing-and-deletion";
  body: string;
  collection: "docs";
  data: InferEntrySchema<"docs">
} & { render(): Render[".mdx"] };
"restrict-moving-messages.mdx": {
	id: "restrict-moving-messages.mdx";
  slug: "restrict-moving-messages";
  body: string;
  collection: "docs";
  data: InferEntrySchema<"docs">
} & { render(): Render[".mdx"] };
"restrict-name-and-email-changes.mdx": {
	id: "restrict-name-and-email-changes.mdx";
  slug: "restrict-name-and-email-changes";
  body: string;
  collection: "docs";
  data: InferEntrySchema<"docs">
} & { render(): Render[".mdx"] };
"restrict-permissions-of-new-members.mdx": {
	id: "restrict-permissions-of-new-members.mdx";
  slug: "restrict-permissions-of-new-members";
  body: string;
  collection: "docs";
  data: InferEntrySchema<"docs">
} & { render(): Render[".mdx"] };
"restrict-profile-picture-changes.mdx": {
	id: "restrict-profile-picture-changes.mdx";
  slug: "restrict-profile-picture-changes";
  body: string;
  collection: "docs";
  data: InferEntrySchema<"docs">
} & { render(): Render[".mdx"] };
"restrict-wildcard-mentions.mdx": {
	id: "restrict-wildcard-mentions.mdx";
  slug: "restrict-wildcard-mentions";
  body: string;
  collection: "docs";
  data: InferEntrySchema<"docs">
} & { render(): Render[".mdx"] };
"review-your-organization-settings.mdx": {
	id: "review-your-organization-settings.mdx";
  slug: "review-your-organization-settings";
  body: string;
  collection: "docs";
  data: InferEntrySchema<"docs">
} & { render(): Render[".mdx"] };
"review-your-settings.mdx": {
	id: "review-your-settings.mdx";
  slug: "review-your-settings";
  body: string;
  collection: "docs";
  data: InferEntrySchema<"docs">
} & { render(): Render[".mdx"] };
"roles-and-permissions.mdx": {
	id: "roles-and-permissions.mdx";
  slug: "roles-and-permissions";
  body: string;
  collection: "docs";
  data: InferEntrySchema<"docs">
} & { render(): Render[".mdx"] };
"saml-authentication.mdx": {
	id: "saml-authentication.mdx";
  slug: "saml-authentication";
  body: string;
  collection: "docs";
  data: InferEntrySchema<"docs">
} & { render(): Render[".mdx"] };
"schedule-a-message.mdx": {
	id: "schedule-a-message.mdx";
  slug: "schedule-a-message";
  body: string;
  collection: "docs";
  data: InferEntrySchema<"docs">
} & { render(): Render[".mdx"] };
"scim.mdx": {
	id: "scim.mdx";
  slug: "scim";
  body: string;
  collection: "docs";
  data: InferEntrySchema<"docs">
} & { render(): Render[".mdx"] };
"search-for-messages.mdx": {
	id: "search-for-messages.mdx";
  slug: "search-for-messages";
  body: string;
  collection: "docs";
  data: InferEntrySchema<"docs">
} & { render(): Render[".mdx"] };
"self-hosted-billing.mdx": {
	id: "self-hosted-billing.mdx";
  slug: "self-hosted-billing";
  body: string;
  collection: "docs";
  data: InferEntrySchema<"docs">
} & { render(): Render[".mdx"] };
"set-default-channels-for-new-users.mdx": {
	id: "set-default-channels-for-new-users.mdx";
  slug: "set-default-channels-for-new-users";
  body: string;
  collection: "docs";
  data: InferEntrySchema<"docs">
} & { render(): Render[".mdx"] };
"set-up-integrations.mdx": {
	id: "set-up-integrations.mdx";
  slug: "set-up-integrations";
  body: string;
  collection: "docs";
  data: InferEntrySchema<"docs">
} & { render(): Render[".mdx"] };
"set-up-your-account.mdx": {
	id: "set-up-your-account.mdx";
  slug: "set-up-your-account";
  body: string;
  collection: "docs";
  data: InferEntrySchema<"docs">
} & { render(): Render[".mdx"] };
"setting-up-zulip-for-a-class.mdx": {
	id: "setting-up-zulip-for-a-class.mdx";
  slug: "setting-up-zulip-for-a-class";
  body: string;
  collection: "docs";
  data: InferEntrySchema<"docs">
} & { render(): Render[".mdx"] };
"share-and-upload-files.mdx": {
	id: "share-and-upload-files.mdx";
  slug: "share-and-upload-files";
  body: string;
  collection: "docs";
  data: InferEntrySchema<"docs">
} & { render(): Render[".mdx"] };
"spoilers.mdx": {
	id: "spoilers.mdx";
  slug: "spoilers";
  body: string;
  collection: "docs";
  data: InferEntrySchema<"docs">
} & { render(): Render[".mdx"] };
"star-a-message.mdx": {
	id: "star-a-message.mdx";
  slug: "star-a-message";
  body: string;
  collection: "docs";
  data: InferEntrySchema<"docs">
} & { render(): Render[".mdx"] };
"start-a-call.mdx": {
	id: "start-a-call.mdx";
  slug: "start-a-call";
  body: string;
  collection: "docs";
  data: InferEntrySchema<"docs">
} & { render(): Render[".mdx"] };
"starting-a-new-direct-message.mdx": {
	id: "starting-a-new-direct-message.mdx";
  slug: "starting-a-new-direct-message";
  body: string;
  collection: "docs";
  data: InferEntrySchema<"docs">
} & { render(): Render[".mdx"] };
"status-and-availability.mdx": {
	id: "status-and-availability.mdx";
  slug: "status-and-availability";
  body: string;
  collection: "docs";
  data: InferEntrySchema<"docs">
} & { render(): Render[".mdx"] };
"support-zulip-project.mdx": {
	id: "support-zulip-project.mdx";
  slug: "support-zulip-project";
  body: string;
  collection: "docs";
  data: InferEntrySchema<"docs">
} & { render(): Render[".mdx"] };
"supported-browsers.mdx": {
	id: "supported-browsers.mdx";
  slug: "supported-browsers";
  body: string;
  collection: "docs";
  data: InferEntrySchema<"docs">
} & { render(): Render[".mdx"] };
"switching-between-organizations.mdx": {
	id: "switching-between-organizations.mdx";
  slug: "switching-between-organizations";
  body: string;
  collection: "docs";
  data: InferEntrySchema<"docs">
} & { render(): Render[".mdx"] };
"tables.mdx": {
	id: "tables.mdx";
  slug: "tables";
  body: string;
  collection: "docs";
  data: InferEntrySchema<"docs">
} & { render(): Render[".mdx"] };
"text-emphasis.mdx": {
	id: "text-emphasis.mdx";
  slug: "text-emphasis";
  body: string;
  collection: "docs";
  data: InferEntrySchema<"docs">
} & { render(): Render[".mdx"] };
"topic-notifications.mdx": {
	id: "topic-notifications.mdx";
  slug: "topic-notifications";
  body: string;
  collection: "docs";
  data: InferEntrySchema<"docs">
} & { render(): Render[".mdx"] };
"trying-out-zulip.mdx": {
	id: "trying-out-zulip.mdx";
  slug: "trying-out-zulip";
  body: string;
  collection: "docs";
  data: InferEntrySchema<"docs">
} & { render(): Render[".mdx"] };
"typing-notifications.mdx": {
	id: "typing-notifications.mdx";
  slug: "typing-notifications";
  body: string;
  collection: "docs";
  data: InferEntrySchema<"docs">
} & { render(): Render[".mdx"] };
"unsubscribe-from-a-channel.mdx": {
	id: "unsubscribe-from-a-channel.mdx";
  slug: "unsubscribe-from-a-channel";
  body: string;
  collection: "docs";
  data: InferEntrySchema<"docs">
} & { render(): Render[".mdx"] };
"user-cards.mdx": {
	id: "user-cards.mdx";
  slug: "user-cards";
  body: string;
  collection: "docs";
  data: InferEntrySchema<"docs">
} & { render(): Render[".mdx"] };
"user-groups.mdx": {
	id: "user-groups.mdx";
  slug: "user-groups";
  body: string;
  collection: "docs";
  data: InferEntrySchema<"docs">
} & { render(): Render[".mdx"] };
"user-list.mdx": {
	id: "user-list.mdx";
  slug: "user-list";
  body: string;
  collection: "docs";
  data: InferEntrySchema<"docs">
} & { render(): Render[".mdx"] };
"using-zulip-for-a-class.mdx": {
	id: "using-zulip-for-a-class.mdx";
  slug: "using-zulip-for-a-class";
  body: string;
  collection: "docs";
  data: InferEntrySchema<"docs">
} & { render(): Render[".mdx"] };
"using-zulip-via-email.mdx": {
	id: "using-zulip-via-email.mdx";
  slug: "using-zulip-via-email";
  body: string;
  collection: "docs";
  data: InferEntrySchema<"docs">
} & { render(): Render[".mdx"] };
"verify-your-message-was-successfully-sent.mdx": {
	id: "verify-your-message-was-successfully-sent.mdx";
  slug: "verify-your-message-was-successfully-sent";
  body: string;
  collection: "docs";
  data: InferEntrySchema<"docs">
} & { render(): Render[".mdx"] };
"view-a-messages-edit-history.mdx": {
	id: "view-a-messages-edit-history.mdx";
  slug: "view-a-messages-edit-history";
  body: string;
  collection: "docs";
  data: InferEntrySchema<"docs">
} & { render(): Render[".mdx"] };
"view-all-bots-in-your-organization.mdx": {
	id: "view-all-bots-in-your-organization.mdx";
  slug: "view-all-bots-in-your-organization";
  body: string;
  collection: "docs";
  data: InferEntrySchema<"docs">
} & { render(): Render[".mdx"] };
"view-and-edit-your-message-drafts.mdx": {
	id: "view-and-edit-your-message-drafts.mdx";
  slug: "view-and-edit-your-message-drafts";
  body: string;
  collection: "docs";
  data: InferEntrySchema<"docs">
} & { render(): Render[".mdx"] };
"view-channel-subscribers.mdx": {
	id: "view-channel-subscribers.mdx";
  slug: "view-channel-subscribers";
  body: string;
  collection: "docs";
  data: InferEntrySchema<"docs">
} & { render(): Render[".mdx"] };
"view-images-and-videos.mdx": {
	id: "view-images-and-videos.mdx";
  slug: "view-images-and-videos";
  body: string;
  collection: "docs";
  data: InferEntrySchema<"docs">
} & { render(): Render[".mdx"] };
"view-messages-sent-by-a-user.mdx": {
	id: "view-messages-sent-by-a-user.mdx";
  slug: "view-messages-sent-by-a-user";
  body: string;
  collection: "docs";
  data: InferEntrySchema<"docs">
} & { render(): Render[".mdx"] };
"view-someones-profile.mdx": {
	id: "view-someones-profile.mdx";
  slug: "view-someones-profile";
  body: string;
  collection: "docs";
  data: InferEntrySchema<"docs">
} & { render(): Render[".mdx"] };
"view-the-exact-time-a-message-was-sent.mdx": {
	id: "view-the-exact-time-a-message-was-sent.mdx";
  slug: "view-the-exact-time-a-message-was-sent";
  body: string;
  collection: "docs";
  data: InferEntrySchema<"docs">
} & { render(): Render[".mdx"] };
"view-the-markdown-source-of-a-message.mdx": {
	id: "view-the-markdown-source-of-a-message.mdx";
  slug: "view-the-markdown-source-of-a-message";
  body: string;
  collection: "docs";
  data: InferEntrySchema<"docs">
} & { render(): Render[".mdx"] };
"view-your-bots.mdx": {
	id: "view-your-bots.mdx";
  slug: "view-your-bots";
  body: string;
  collection: "docs";
  data: InferEntrySchema<"docs">
} & { render(): Render[".mdx"] };
"view-your-mentions.mdx": {
	id: "view-your-mentions.mdx";
  slug: "view-your-mentions";
  body: string;
  collection: "docs";
  data: InferEntrySchema<"docs">
} & { render(): Render[".mdx"] };
"view-zulip-version.mdx": {
	id: "view-zulip-version.mdx";
  slug: "view-zulip-version";
  body: string;
  collection: "docs";
  data: InferEntrySchema<"docs">
} & { render(): Render[".mdx"] };
"zulip-cloud-billing.mdx": {
	id: "zulip-cloud-billing.mdx";
  slug: "zulip-cloud-billing";
  body: string;
  collection: "docs";
  data: InferEntrySchema<"docs">
} & { render(): Render[".mdx"] };
"zulip-cloud-or-self-hosting.mdx": {
	id: "zulip-cloud-or-self-hosting.mdx";
  slug: "zulip-cloud-or-self-hosting";
  body: string;
  collection: "docs";
  data: InferEntrySchema<"docs">
} & { render(): Render[".mdx"] };
};

	};

	type DataEntryMap = {
		
	};

	type AnyEntryMap = ContentEntryMap & DataEntryMap;

	export type ContentConfig = typeof import("../src/content/config.js");
}
