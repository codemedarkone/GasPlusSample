#include "Meta/MetaAttributes.h"

#if __has_include("HAL/CriticalSection.h")
#include "HAL/CriticalSection.h"
#include "Misc/ScopeLock.h"
#else
#include <mutex>
#endif

namespace GasPlusSample::Attributes::Meta
{
#if !__has_include("HAL/CriticalSection.h")
    class FCriticalSection
    {
    public:
        void Lock()
        {
            Mutex.lock();
        }

        void Unlock()
        {
            Mutex.unlock();
        }

    private:
        std::mutex Mutex;
    };

    class FScopeLock
    {
    public:
        explicit FScopeLock(FCriticalSection* InCriticalSection)
            : CriticalSection(InCriticalSection)
        {
            if (CriticalSection)
            {
                CriticalSection->Lock();
            }
        }

        ~FScopeLock()
        {
            if (CriticalSection)
            {
                CriticalSection->Unlock();
            }
        }

    private:
        FCriticalSection* CriticalSection;
    };
#endif

    namespace
    {
        FCriticalSection GMetaAttributesRegistryMutex;
    }

    const FMetaRegistryName FMetaAttributesRegistry::DamageKey(TEXT("Damage"));
    const FMetaRegistryName FMetaAttributesRegistry::HealKey(TEXT("Heal"));
    const FMetaRegistryName FMetaAttributesRegistry::ShieldDeltaKey(TEXT("ShieldDelta"));

    FMetaAttributeDefinition::FMetaAttributeDefinition(
        const FMetaRegistryName& InRegistryName,
        const FMetaRegistryName& InBackingAttributeName,
        const FMetaRegistryString& InDescription)
        : RegistryName(InRegistryName)
        , BackingAttributeName(InBackingAttributeName)
        , Description(InDescription)
    {
    }

    const FMetaAttributesRegistry& FMetaAttributesRegistry::Get()
    {
        static FMetaAttributesRegistry Instance;
        return Instance;
    }

    void FMetaAttributesRegistry::RegisterEditorExtension(const FMetaAttributeDefinition& Definition)
    {
        FScopeLock Lock(&GMetaAttributesRegistryMutex);
        FMetaAttributesRegistry& Registry = const_cast<FMetaAttributesRegistry&>(Get());
        Registry.Register(Definition);
    }

    FMetaAttributesRegistry::FMetaAttributesRegistry()
    {
        Register(FMetaAttributeDefinition(DamageKey, DamageKey, TEXT("Aggregates outgoing damage modifications before final application.")));
        Register(FMetaAttributeDefinition(HealKey, HealKey, TEXT("Aggregates incoming healing before it is applied to core attributes.")));
        Register(FMetaAttributeDefinition(ShieldDeltaKey, ShieldDeltaKey, TEXT("Captures shield-specific adjustments that may bypass health values.")));
    }

    void FMetaAttributesRegistry::Register(const FMetaAttributeDefinition& Definition)
    {
        if (Definition.RegistryName.IsNone() || Definitions.Contains(Definition.RegistryName))
        {
            return;
        }

        Definitions.Add(Definition.RegistryName, Definition);
    }

    const TMetaRegistryMap<FMetaRegistryName, FMetaAttributeDefinition>& FMetaAttributesRegistry::GetDefinitions() const
    {
        return Definitions;
    }

    const FMetaAttributeDefinition* FMetaAttributesRegistry::FindDefinition(const FMetaRegistryName& RegistryName) const
    {
        return Definitions.Find(RegistryName);
    }

    const FMetaAttributeDefinition& FMetaAttributesRegistry::GetDamage() const
    {
        return Definitions.FindChecked(DamageKey);
    }

    const FMetaAttributeDefinition& FMetaAttributesRegistry::GetHeal() const
    {
        return Definitions.FindChecked(HealKey);
    }

    const FMetaAttributeDefinition& FMetaAttributesRegistry::GetShieldDelta() const
    {
        return Definitions.FindChecked(ShieldDeltaKey);
    }
}
